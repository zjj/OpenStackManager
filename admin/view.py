import os
import web
from web.utils import Storage
from model import * 
from auth import get_username, get_userid
from api.fakeopenstack import *

urls = (
        "", "Admin",
        "/check", "Check",
        "/delete", "Delete",
)

def csrf_token():
    if not web.ctx.session.has_key('csrf_token'):
        from uuid import uuid4
        web.ctx.session.csrf_token=uuid4().hex
    return web.ctx.session.csrf_token

def csrf_protected(f):
    def decorated(*args,**kwargs):
        inp = web.input()
        if not (inp.has_key('csrf_token') and inp.csrf_token==web.ctx.session.pop('csrf_token',None)):
            raise web.seeother("")
        return f(*args,**kwargs)
    return decorated

t_globals = {'csrf':csrf_token, 'get_username':get_username, 'get_userid':get_userid}

mdir = os.path.dirname(__file__)
render = web.template.render('%s/templates/'%(mdir), base='base', globals=t_globals)

class Admin:
    def GET(self):
        userid = web.ctx.session.get('userid', -1)
        if userid == -1:
            raise web.seeother("/index", absolute=True)
        username = get_username(userid=userid)
        all_pending_servers = get_all_pending_servers().list()
        all_running_servers = get_tenant_servers(tenant_name=os_tenant_name)
        images = get_images(os_tenant_name)
        images_dict = dict([(i.id, i.name) for i in images])
        flavors = get_flavors(os_tenant_name)
        flavors_dict = dict([(f.id,'cpus:%s ram:%s disk:%s'%(f.vcpus, f.ram, f.disk)) for f in flavors])
        tenants_dict = dict([(t.id, t.name) for t in get_all_tenants()]) 
        ctx = Storage(locals()) 
        return render.admin(ctx)
    
    def POST(self):
        pass

class Check:
    @csrf_protected
    def POST(self): 
        request = web.input()
        try:
            del request['csrf_token']
        except:
            pass
        for i in request:
            if request[i] == u'reject':
                delete_pending_server(i)
            elif request[i] == u'accept':
                ns = get_pending_server_info(i).list()[0]
                create_server(ns.server_name, ns.image,  ns.flavor,  get_username(ns.user))
                delete_pending_server(i)

        raise web.seeother("/admin", absolute=True)

class Delete:
    @csrf_protected
    def POST(self): 
        servers_id = []
        request = web.input()
        try:
            del request['csrf_token']
        except:
            pass
        for i in request:
            if request[i] == u'delete':
                servers_id.append(i)
        #FIXME
        #here we need a synchronous,or the admin page would still show the deleted servers
        #I have to refresh the page
        delete_servers(servers_id) 
        raise web.seeother("/admin", absolute=True)

admin_app = web.application(urls, locals(), autoreload=True)