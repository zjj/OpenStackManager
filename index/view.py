# -*- coding: UTF-8 -*- 
import os
import web
from model import get_page
from auth import get_username
from markdown import markdown

urls = (
    '', 'index',
)

t_globals ={'markdown': markdown,}

mdir = os.path.dirname(__file__)
render = web.template.render('%s/templates/'%(mdir),globals=t_globals)

class index:
    def GET(self):
        userid = web.ctx.session.get('userid',-1)
        username = get_username(userid=userid)
        ctx = get_page()
        ctx.update(userid=userid)
        ctx.update(username=username)
        return render.index(ctx)

index_app = web.application(urls, locals())
