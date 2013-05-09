from keystoneclient.v2_0 import client as keystone_client
from novaclient.v1_1 import client as nova_client
import ConfigParser

keystone_config = ConfigParser.ConfigParser()
keystone_config.read('settings.conf')
auth_url = keystone_config.get('keystone','auth_url')
username = keystone_config.get('keystone','username')
password = keystone_config.get('keystone','password')
os_tenant_name = keystone_config.get('keystone','os_tenant_name')

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
    for s in all_servers:
        if getattr(s, "OS-EXT-STS:power_state", 0) == 1 and s.status == 'ACTIVE':    #running and active
            running_servers.append(s)
    return running_servers

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

    
# NEED TO BE IMPROVED ?
# Here tenant_name is going to be the keypair name,
# one tenant <--> one keypair for temporarily.
# name, keypair name, tenant_name are the same value.
def import_pubkey(name, pub_key=None):
    nc = nova_client.Client(username, password, name, auth_url, service_type="compute")
    newkeypair = nc.keypairs.create(name, pub_key)
    return newkeypair 

def fingerprint(name):
    nc = nova_client.Client(username, password, name, auth_url, service_type="compute")
    keypairs = nc.keypairs.list()
    for k in keypairs:
        if k.name == name:
            return k.fingerprint
    

def delete_pubkey(name):
    nc = nova_client.Client(username, password, name, auth_url, service_type="compute")
    keypairs = nc.keypairs.list()
    for k in keypairs:
        if k.name == name:
            k.delete()
            break
