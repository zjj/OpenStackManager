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
    mykeystone = keystone_client.Client(username=username,
                     password=password, tenant_name=os_tenant_name, auth_url=auth_url)
    tenants = mykeystone.tenants.list()
    if len(tenants) != 0:
        my_tenant = [x for x in tenants if x.name==tenant_name]
        if len(my_tenant) != 0:
            return my_tenant[0].id
    return None

def get_role_id(role_name=None):
    mykeystone = keystone_client.Client(username=username,
                     password=password, tenant_name=os_tenant_name, auth_url=auth_url)
    roles = mykeystone.roles.list()
    for role in roles:
        if role.name == role_name:
            return role.id
    return -1

def get_keystoneuser_id(username=None):
    mykeystone = keystone_client.Client(username=username,
                     password=password, tenant_name=os_tenant_name, auth_url=auth_url)
    users = mykeystone.users.list()
    for user in users:
        if user.name == username:
            return user.id
    return -1  

def get_tenant_servers(tenant_name=None):
    mynova = nova_client.Client(username, password, tenant_name, auth_url, service_type="compute")
    search_opts = {'tenant_id':get_tenant_id(tenant_name)}
    servers = mynova.servers.list(search_opts=search_opts)
    return servers

def get_images(tenant_name=None):
    mynova = nova_client.Client(username, password, tenant_name, auth_url, service_type="compute")
    return mynova.images.list()

def get_flavors(tenant_name=None):
    mynova = nova_client.Client(username, password, tenant_name, auth_url, service_type="compute")
    return mynova.flavors.list()

#TODO
def create_server(name, image, flavor, tenant_name):
    mynova = nova_client.Client(username, password, tenant_name, auth_url, service_type="compute")
    return mynova.servers.create(name, image, flavor)
    
def create_tenant(name):
    mykeystone = keystone_client.Client(username=username,
                     password=password, tenant_name=os_tenant_name,auth_url=auth_url)
    newtenant = mykeystone.tenants.create(name)
    return newtenant


