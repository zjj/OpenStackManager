from keystoneclient.v2_0 import client as keystone_client
from novaclient.v1_1 import client as nova_client
import ConfigParser

keystone_config = ConfigParser.ConfigParser()
keystone_config.read('settings.conf')
auth_url = keystone_config.get('keystone','auth_url')
username = keystone_config.get('keystone','username')
password = keystone_config.get('keystone','password')
mykeystone = keystone_client.Client(username=username, password=password, auth_url=auth_url)

def get_tenant_id(tenant_name=None):
    tenants = mykeystone.tenants.list()
    if len(tenants) != 0:
        my_tenant = [x for x in tenants if x.name==tenant_name]
        if len(my_tenant) != 0:
            return my_tenant[0].id
    return None

def get_tenant_servers(tenant_id=None):
    mynova = nova_client.Client(username, password, tenant_id, auth_url, service_type="compute")
    search_opts = {'all_tenants':True}
    servers = mynova.servers.list(search_opts=search_opts)
    if len(servers) != 0:
        tenant_servers = [x for x in servers if x.tenant_id == tenant_id]
        return tenant_servers
    return []

def get_images(tenant_id=None):
    mynova = nova_client.Client(username, password, tenant_id, auth_url, service_type="compute")
    return mynova.images.list()
