# -*- coding: UTF-8 -*- 
import os
import web
from web.utils import Storage
from model import get_page, update_index_page
from auth import get_username, get_userid, is_superuser
from markdown import markdown
from i18n import custom_gettext as _ 

urls = (
    '', 'index',
    '/edit','Edit',
    '/lang','Lang',
)

t_globals ={'markdown': markdown, 
            'True': True,
            '_': _}

mdir = os.path.dirname(__file__)
render = web.template.render('%s/templates/'%(mdir), base="base", globals=t_globals)

class index:
    def GET(self):
        userid = web.ctx.session.get('userid',-1)
        username = get_username(userid=userid)
        superuser = is_superuser(userid=userid)
        index_wiki = get_page()
        ctx = Storage(locals())
        return render.index(ctx)


class Lang:
    def GET(self):
        i = web.input()
        lang = i.get('lang')
        if lang:
            web.ctx.session['lang'] = lang
        raise web.seeother("/index", absolute=True)   

class Edit:
    def GET(self):
        userid = web.ctx.session.get('userid',-1)
        superuser = is_superuser(userid=userid)
        if not is_superuser(userid):
            raise web.seeother("/index", absolute=True)
        username = get_username(userid=userid)
        index_wiki = get_page()
        ctx = Storage(locals())
        return render.edit_index(ctx) 
        
    def POST(self):
        request = web.input()
        index_wiki = request.index_wiki
        update_index_page(index_wiki)
        raise web.seeother("/")
        

index_app = web.application(urls, locals())
