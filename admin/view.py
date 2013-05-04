import os
import web
from web.utils import Storage
from model import * 
from auth import get_username, get_userid
from home.fakeopenstack import *

urls = (
        "", "Admin",
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

admin_app = web.application(urls, locals(), autoreload=True)
