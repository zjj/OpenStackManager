import os
import web
from model import get_servers, add_server
from auth import get_username, get_userid
from web.utils import Storage
from api.fakeopenstack import *

urls = (
    '', 'Home',
    '/ssh', 'Ssh',
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
        image_id = request.image_id
        flavor = request.flavor
        server_name = request.server_name
        add_server(userid, server_name, image_id, flavor)        
        return request

class Ssh:
    def GET(self):
        userid = web.ctx.session.get('userid',-1)
        if userid == -1:
            raise web.seeother('/index', absolute=True)
        username = get_username(userid=userid)
        tenant_name = username
        ctx = Storage(locals())
        return render.ssh(ctx)
    
    @csrf_protected
    def POST(self):
        userid = web.ctx.session.get('userid',-1)
        if userid == -1:
            raise web.seeother('/index', absolute=True)
        username = get_username(userid=userid)

        request = web.input()
        ssh_key = request.ssh_key
        if ssh_key != '':
            if not (ssh_key.startswith("ssh-rsa") or ssh_key.startswith("ssh-dss")):
                return "SSH INPUT ERROR"
            else:
                import_pubkey(username,pub_key=ssh_key)
                raise web.seeother('/home', absolute=True)
        else:
            npk = import_pubkey(username,pub_key=None)
            private_key = npk.private_key
        
        ctx = Storage(locals())
        return render.private_key(ctx)
              
home_app = web.application(urls, locals(), autoreload=True)
