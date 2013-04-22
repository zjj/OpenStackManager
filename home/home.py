import os
import web
from model import get_servers
from auth import get_username
from web.utils import Storage

urls = (
    '','Home',
)

mdir = os.path.dirname(__file__)
render = web.template.render('%s/templates/'%(mdir), base='base')

class Home:
    def GET(self):
        userid = web.ctx.session.get('userid',-1)
        if userid == -1:
            web.seeother('/index', absolute=True)
        username = get_username(userid=userid)
        servers = get_servers(userid)
        ctx = Storage(username=username,servers=servers)
        return render.home(ctx)

home_app = web.application(urls, locals(), autoreload=True)
