import os
import web
from model import get_servers, add_server, delete_server
from auth import get_username, get_userid, is_superuser
from web.utils import Storage
from lib.fakeopenstack import *
from lib.utils import csrf_token, csrf_protected, login_required
from i18n import custom_gettext as _

urls = (
    '', 'Home',
    '/apply', 'Apply',
    '/add_floatingip', 'FloatingIp',
)

t_globals = {'csrf':csrf_token, '_':_, 'getattr':getattr}

mdir = os.path.dirname(__file__)
render = web.template.render('%s/templates/'%(mdir), base='base',globals=t_globals)


class FloatingIp:
    def GET(self):
        return 'nothing to get :)'
    
    @login_required
    @csrf_protected
    def POST(self):
        userid = web.ctx.session.get('userid',-1)
        username = get_username(userid=userid)
        inp = web.input()
        inp.pop('csrf_token', None)
         
        server_floating = dict((floatingip, server_id) for floatingip, \
                                server_id in inp.iteritems() if inp[floatingip]!='')

        for floatingip , server_id in server_floating.iteritems():     
            bind_floatingip(username, server_id, floatingip)

        raise web.seeother("/home", absolute=True)

class Home:
    @login_required
    def GET(self):
        userid = web.ctx.session.get('userid',-1)
        superuser = is_superuser(userid)
        username = get_username(userid=userid)
        tenant_name = username
        servers = get_servers(userid).list()
        running_servers = get_tenant_servers_db(tenant_name)
        images_dict = get_images_dict_db()
        servers_x = []
        for server in servers:
            if server.image not in images_dict:
                delete_server(image=server.image) 
            else:
                servers_x.append(server)
        servers = servers_x
        flavors_dict = get_flavors_dict_db()
        floating_ips = get_floatingips_db(tenant_name)
        ctx = Storage(locals())
        return render.home(ctx)

    @csrf_protected
    def POST(self):
        to_delete_servers=[]
        to_reboot_servers=[]
        request = web.input()
        try:
            del request['csrf_token']
        except:
            pass 
        for i in request:
            if request[i] == u'delete':
                to_delete_servers.append(i)
            elif request[i] == u'reboot':
                to_reboot_servers.append(i)
        reboot_servers(to_reboot_servers)
        delete_servers(to_delete_servers)
        raise web.seeother("/home", absolute=True)
        
class Apply:
    @keypair_required
    @csrf_protected
    def POST(self):
        userid = web.ctx.session.get('userid',-1)
        request = web.input()
        image_id = request.image_id
        flavor = request.flavor
        server_name = request.server_name
        add_server(userid, server_name, image_id, flavor)        
        raise web.seeother("/home", absolute=True)

home_app = web.application(urls, locals(), autoreload=True)
