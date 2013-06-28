from keystoneclient.v2_0 import client as keystone_client
from novaclient.v1_1 import client as nova_client
from auth.model import get_username
import ConfigParser
import web
from i18n import custom_gettext as _

keystone_config = ConfigParser.ConfigParser()
keystone_config.read('settings.conf')
auth_url = keystone_config.get('keystone','auth_url')
username = keystone_config.get('keystone','username')
password = keystone_config.get('keystone','password')
os_tenant_name = keystone_config.get('keystone','os_tenant_name')

def security_ports_filter(security_ports=[]):
    ret = []
    for i in security_ports:
        try:
            ret.append(str(int(i)))
        except ValueError:
            pass
    return ret
              
security_ports = security_ports_filter(keystone_config.get('nova','security_ports').split(','))


def get_tenant_id(tenant_name=None):
    kc = keystone_client.Client(username=username,
                     password=password, tenant_name=os_tenant_name, auth_url=auth_url)
    tenants = kc.tenants.list()
    if len(tenants) != 0:
        my_tenant = [x for x in tenants if x.name==tenant_name]
        if len(my_tenant) != 0:
            return my_tenant[0].id
    return None

def get_tenant_name(tenant_id):
    kc = keystone_client.Client(username=username,
                     password=password, tenant_name=os_tenant_name, auth_url=auth_url)
    tenants = kc.tenants.list()
    for tenant in tenants:
        if tenant.id == tenant_id:
            return tenant.name
    return None

def get_all_tenants():
    kc = keystone_client.Client(username=username,
                     password=password, tenant_name=os_tenant_name, auth_url=auth_url)
    return kc.tenants.list()

def get_role_id(role_name=None):
    kc = keystone_client.Client(username=username,
                     password=password, tenant_name=os_tenant_name, auth_url=auth_url)
    roles = kc.roles.list()
    for role in roles:
        if role.name == role_name:
            return role.id
    return -1

def get_keystoneuser_id(username=None):
    kc = keystone_client.Client(username=username,
                     password=password, tenant_name=os_tenant_name, auth_url=auth_url)
    users = kc.users.list()
    for user in users:
        if user.name == username:
            return user.id
    return -1  

def get_tenant_servers(tenant_name=None):
    nc = nova_client.Client(username, password, tenant_name, auth_url, service_type="compute")
    if tenant_name == os_tenant_name: 
        search_opts = {'all_tenants':True}
    else:
        search_opts = {'tenant_id':get_tenant_id(tenant_name)}
    all_servers = nc.servers.list(search_opts=search_opts)
    running_servers = []
    if tenant_name != os_tenant_name:
        for s in all_servers:
            if getattr(s, "OS-EXT-STS:power_state", 0) == 1 and s.status == 'ACTIVE':    #running and active
                running_servers.append(s)
    else:
        running_servers = all_servers
        #for s in all_servers:
        #    if getattr(s, "OS-EXT-STS:power_state", 0) == 1:
        #        running_servers.append(s)
    return running_servers

def get_server_status(server_list=[]):
    status_dict={}
    nc = nova_client.Client(username, password, os_tenant_name, auth_url, service_type="compute")
    search_opts = {'all_tenants':True}
    servers = nc.servers.list(search_opts=search_opts)
    for s in servers:
        if s.id in server_list:
            stat = getattr(s, 'OS-EXT-STS:task_state', None)
            if not stat:
                stat = getattr(s, 'OS-EXT-STS:vm_state', None)
            status_dict.update({s.id:_(stat)})
    return status_dict
            
def get_images(tenant_name=None):
    nc = nova_client.Client(username, password, tenant_name, auth_url, service_type="compute")
    return nc.images.list()

def get_flavors(tenant_name=None):
    nc = nova_client.Client(username, password, tenant_name, auth_url, service_type="compute")
    return nc.flavors.list()

#TODO 
#x = create_server('dsdddd', '30de55f0-aad5-4ec2-8f67-be8e510e02fd',  1,  'jj')
def create_server(name, image, flavor, tenant_name):
    nc = nova_client.Client(username, password, tenant_name, auth_url, service_type="compute")
    return nc.servers.create(name, image, flavor, key_name=tenant_name)

def create_floatingip(tenant_name):
    nc = nova_client.Client(username, password, tenant_name, auth_url, service_type="compute")
    return nc.floating_ips.create()

def get_floatingips(tenant_name):
    nc = nova_client.Client(username, password, tenant_name, auth_url, service_type="compute")
    return nc.floating_ips.list()

def bind_floatingip(tenant_name, server_id, floatingip):
    nc = nova_client.Client(username, password, tenant_name, auth_url, service_type="compute")
    floatingips = nc.floating_ips.list()
    for fi in floatingips:
        if fi.ip == floatingip:
            FloatingIP = fi
            break
    
    if FloatingIP.instance_id and FloatingIP.instance_id != server_id:#@@ unbind floating ip if bound
        s = nc.servers.get(FloatingIP.instance_id)
        s.remove_floating_ip(FloatingIP)

    if FloatingIP.instance_id != server_id:
        server = nc.servers.get(server_id)
        server.add_floating_ip(FloatingIP) 

def delete_servers(server_id=[]):
    nc = nova_client.Client(username, password, os_tenant_name, auth_url, service_type="compute")
    search_opts = {'all_tenants':True}
    servers = nc.servers.list(search_opts=search_opts)
    for s in servers:
        if s.id in server_id:
            s.delete()

def reboot_servers(server_id=[]):
    nc = nova_client.Client(username, password, os_tenant_name, auth_url, service_type="compute")
    search_opts = {'all_tenants':True}
    servers = nc.servers.list(search_opts=search_opts)
    for s in servers:
        if s.id in server_id:
            s.reboot()

def create_tenant(name):
    kc = keystone_client.Client(username=username,
                     password=password, tenant_name=os_tenant_name,auth_url=auth_url)
    newtenant = kc.tenants.create(name)
    return newtenant

def create_default_security_group_rules(tenant_name):
    nc = nova_client.Client(username, password, tenant_name, auth_url, service_type="compute")
    global security_ports
    sg = nc.security_groups.api.security_groups.list()[0] #we only use the first security group
    sg_id = sg.id
    sgr = nc.security_group_rules
    try:
        sgr.create(sg_id, 'icmp', from_port='-1', to_port='-1', cidr='0.0.0.0/0')
    except:
        pass
    for port in security_ports:
        try:
            sgr.create(sg_id, 'tcp', from_port=port, to_port=port, cidr='0.0.0.0/0')  
        except:
            pass

# NEED TO BE IMPROVED ?
# Here tenant_name is going to be the keypair name,
# one tenant <--> one keypair for temporarily.
# name, keypair name, tenant_name are the same value.
def import_pubkey(name, tenant_name=None, pub_key=None):
    if tenant_name == None:
        tenant_name = name
    nc = nova_client.Client(username, password, tenant_name, auth_url, service_type="compute")
    newkeypair = nc.keypairs.create(name, pub_key)
    return newkeypair 

def fingerprint(name):
    nc = nova_client.Client(username, password, name, auth_url, service_type="compute")
    keypairs = nc.keypairs.list()
    for k in keypairs:
        if k.name == name:
            return k.fingerprint
    

def delete_pubkey(name, tenant_name=None):
    if tenant_name == None:
        tenant_name = name
    nc = nova_client.Client(username, password, tenant_name, auth_url, service_type="compute")
    keypairs = nc.keypairs.list()
    for k in keypairs:
        if k.name == name:
            k.delete()
            break

def keypair_required(f):
    def wrap(*args, **kwargs):
        userid = web.ctx.session.get('userid',-1)
        name = get_username(userid=userid)
        nc = nova_client.Client(username, password, name, auth_url, service_type="compute")
        keypairs = nc.keypairs.list()
        exist = False
        for k in keypairs:
            if k.name == name:
                exist = True
                break
        if exist:  
            return f(*args, **kwargs)
        else:
            raise web.seeother("/auth/ssh", absolute=True)
    return wrap

