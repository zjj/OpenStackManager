import os
import sys
import web
from web import form
from web.utils import Storage
from auth import authenticate, get_username, get_userid, get_email, User, email_re, update_email
from lib.fakeopenstack import *
from lib.utils import csrf_token, csrf_protected

mdir = os.path.dirname(__file__)

urls = (
        "", "Login",
        "/login", "Login",
        "/logout", "Logout",
        "/signup", "Signup",
        "/passwd", "Passwd",
        "/ssh", "SSH",
        "/email", "Email",
)

t_globals = {'csrf':csrf_token}

render = web.template.render('%s/templates/'%(mdir))

class Login:
    login_form = form.Form(
        form.Textbox(name='username',size=10),
        form.Password(name='password',size=10),
        form.Button('Login',type='submit'),)

    def GET(self):
        session = web.ctx.session
        if session.get('loggedin',0) == 1:
            raise web.seeother("/index", absolute=True)
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
            raise web.seeother('/index', absolute=True)
        else:
            return "username or password error"

class Logout:
    def GET(self):  
        web.ctx.session.kill()
        raise web.seeother("/index",absolute=True)

class Signup:
    def GET(self):
        session = web.ctx.session
        if session.get('loggedin',0) == 1:
            raise web.seeother("/index", absolute=True)
        return render.signup()

    def POST(self):
        session = web.ctx.session
        request = web.input()
        username = request.username
        password = request.password
        email = request.email
        userid = get_userid(username)
        if userid == -1:
            newuser = User(password=password, username=username, email=email)
            try:
                newuser.save()
            except:
                return "Email exists"
            newtenant = create_tenant(username)
            newtenant.add_user(get_keystoneuser_id(os_tenant_name), 
                                get_role_id('admin'))
        else:
            return "user exists"
        raise web.seeother("/login")

render_fluid = web.template.render('%s/templates/'%(mdir), base="fluid", globals=t_globals)

class Passwd:
    def GET(self):
        userid = web.ctx.session.get('userid',-1)
        if userid == -1:
            raise web.seeother("/login")
        else:
            username = get_username(userid=userid)
            ctx = Storage(locals())
            return render_fluid.change_passwd(ctx)

    def POST(self):
        if web.ctx.session.get('loggedin',0) == 1:
            userid = web.ctx.session.get('userid',-1)
            username = get_username(userid)
        request = web.input()
        old_password = request.old_password
        new_password = request.new_password
        new_password_confirm = request.new_password_confirm
        if new_password != new_password_confirm:
            msg = "Password doesn't match the confirmation"
            error = True
        else:
            user = User(username=username, password=old_password)
            if user.is_authenticated() == True:
                user.set_passwd(new_password)
                user.save(update=True)
                msg = "PassWord Changed!"
                error = False
            else:
                msg = "Old PassWord Error!"
                error = True
        ctx = Storage(locals())
        return render_fluid.msg(ctx)

class SSH:
    def GET(self):
        userid = web.ctx.session.get('userid',-1)
        if userid == -1:
            raise web.seeother('/index', absolute=True)
        username = get_username(userid=userid)
        tenant_name = username
        keypair = fingerprint(tenant_name)
        ctx = Storage(locals())
        return render_fluid.ssh(ctx)
    
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
                msg = "SSH INPUT ERROR"
                error = True
                ctx = Storage(locals())
                return render_fluid.msg(ctx) 
            else:
                try:
                    delete_pubkey(username)
                except:
                    pass
                import_pubkey(username,pub_key=ssh_key)
                raise web.seeother('')
        else:
            try:
                delete_pubkey(username)
            except:
                pass
            npk = import_pubkey(username,pub_key=None)
            private_key = npk.private_key
        
        ctx = Storage(locals())
        return render_fluid.private_key(ctx)

class Email:
    def GET(self):
        userid = web.ctx.session.get('userid',-1)
        if userid == -1:
            raise web.seeother('/index', absolute=True)
        username = get_username(userid=userid)
        email = get_email(userid=userid) 
        ctx = Storage(locals())
        return render_fluid.email(ctx)
    
    def POST(self):
        userid = web.ctx.session.get('userid',-1)
        if userid == -1:
            raise web.seeother('/index', absolute=True)
        username = get_username(userid=userid)
        request = web.input()
        email = request.email
        if email_re.match(email):
            update_email(userid, email)
            email = get_email(userid=userid) 
            ctx = Storage(locals())
            return render_fluid.email(ctx)
        else:
            msg = "Email not valid"
            error = True
            ctx = Storage(locals())
            return render_fluid.msg(ctx)

auth_app = web.application(urls, globals(), autoreload=True)
