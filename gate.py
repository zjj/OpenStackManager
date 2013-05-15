import web
from home import home_app
from index import index_app
from admin import admin_app
from auth import auth_app
from db import db
web.config.debug = False

urls = (
    '/auth', auth_app,
    '/home', home_app,
    '/index', index_app,
    '/admin', admin_app,
    '/', index_app,
    )

app = web.application(urls, globals())
store = web.session.DBStore(db, 'sessions')
session = web.session.Session(app, store, initializer={'loggedin': 0})

def session_hook():
    web.ctx.session = session
app.add_processor(web.loadhook(session_hook))

application = app.wsgifunc()
