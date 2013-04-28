import os
import web
from model import get_servers, add_server
from auth import get_username
from web.utils import Storage
from fakeopenstack import * 

urls = (
    '','Home',
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

t_globals = {'csrf':csrf_token}

mdir = os.path.dirname(__file__)
render = web.template.render('%s/templates/'%(mdir), base='base',globals=t_globals)

class Home:
    def GET(self):
        userid = web.ctx.session.get('userid',-1)
        if userid == -1:
            raise web.seeother('/index', absolute=True)
        username = get_username(userid=userid)
        tenant_name = username
        servers = get_servers(userid).list()
        running_servers = get_tenant_servers(tenant_name)
        images = get_images(tenant_name)
        images_dict = dict([(i.id, i.name) for i in images])
        flavors = get_flavors(tenant_name)
        flavors_dict = dict([(f.id,'cpus:%s ram:%s disk:%s'%(f.vcpus, f.ram, f.disk)) for f in flavors])
        ctx = Storage(locals())
        return render.home(ctx)
    
    @csrf_protected
    def POST(self):
        userid = web.ctx.session.get('userid',-1)
        request = web.input()
        public_key = request.public_key
        image_id = request.image_id
        flavor = request.flavor
        server_name = request.server_name
        add_server(userid, server_name, image_id, flavor, public_key)        
        #create_server(server_name, image_id, flavor)
        return request

home_app = web.application(urls, locals(), autoreload=True)
