import web
from web import form
#
#this is just for exercising ~~
#
web.config.debug = True

urls = ("/admin", "admin",
        "/apply","apply",
)
app = web.application(urls, globals())

db = web.database(dbn='sqlite', db='database/jj')
store = web.session.DBStore(db, 'sessions')
session = web.session.Session(app, store, initializer={'count': 0})
render = web.template.render('templates/')

class admin:
    def GET(self):
        users = db.select('user')
        dir(users)
        return render.users(users)

class apply:
    def GET(self):
        server = form.Form(
            form.Dropdown('os', [('debian', 'Debian'), ('redhat', 'RedHat')]),
            form.Dropdown('cpu', [('1', '1 core'), ('2', '2 cores')]),
            form.Dropdown('flavor', [('1', '512M 1G'),('1024', '1G 1G'), ('2048', '2G 1G')]),
        )
        server = server()
        print str(session.count)
        return render.apply(server)

application = app.wsgifunc()
