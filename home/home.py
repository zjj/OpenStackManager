import os
import web
from model import get_servers
from auth import get_username
from web.utils import Storage

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
        servers = get_servers(userid)
        ctx = Storage(username=username,servers=servers)
        return render.home(ctx)
    
    @csrf_protected
    def POST(self):
        request = web.input()
        for r in request:
            pass    #action
        #raise  web.seeother('')
        return request

            

home_app = web.application(urls, locals(), autoreload=True)
