import os
import sys
import web
from web import form
from auth import authenticate, get_userid, User

mdir = os.path.dirname(__file__)

urls = (
        "", "Login",
        "/login", "Login",
        "/logout", "Logout",
        "/register", "Register",
)

render = web.template.render('%s/templates/'%(mdir))

class Login:
    login_form = form.Form(
        form.Textbox(name='username',size=10),
        form.Password(name='password',size=10),
        form.Button('Login',type='submit'),)

    def GET(self):
        session = web.ctx.session
        if session.get('loggedin',0) == 1:
            raise web.seeother("/home", absolute=True)
        login = self.login_form()
        return render.login(login)

    def POST(self):
        session = web.ctx.session
        input = web.input()
        username = input.username
        password = input.password
        validate = authenticate(passwd=password,username=username)
        if validate:
            userid = get_userid(username)
            session.update({'loggedin':1})
            session.update({'userid':userid})
            raise web.seeother('/home', absolute=True)
        else:
            return "username or password error"

class Logout:
    def GET(self):  
        web.ctx.session.kill()
        raise web.seeother("/index",absolute=True)

class Register:
    def GET(self):
        session = web.ctx.session
        if session.get('loggedin',0) == 1:
            raise web.seeother("/home", absolute=True)
        return render.register()

    def POST(self):
        session = web.ctx.session
        input = web.input()
        username = input.username
        password = input.password
        email = input.email
        userid = get_userid(username)
        if userid == -1:
            newuser = User(password=password, username=username, email=email)
            newuser.save()
        else:
            return "user exists"
        raise web.seeother("/login")

app = web.application(urls, globals(), autoreload=True)
