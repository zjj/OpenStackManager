import os
import sys
import web
from web import form
from web.utils import Storage
from model import authenticate, get_username, get_userid, get_email, User, email_re, username_re, update_email, is_superuser
from model import get_emailid
from lib.fakeopenstack import *
from lib.utils import csrf_token, csrf_protected
from i18n import custom_gettext as _

mdir = os.path.dirname(__file__)

urls = (
        "", "Login",
        "/login", "Login",
        "/logout", "Logout",
        "/signup", "Signup",
        "/passwd", "Passwd",
        "/ssh", "SSH",
        "/email", "Email",
        "/membercheck", "Membercheck",
        "/emailcheck", "Emailcheck",
        "/passwdcheck", "Passwdcheck",
)

t_globals = {'csrf':csrf_token, '_':_}

render = web.template.render('%s/templates/'%(mdir), globals=t_globals)

class Login:
    def GET(self):
        session = web.ctx.session
        if session.get('loggedin',0) == 1:
            raise web.seeother("/index", absolute=True)
        msg = None
        ctx = Storage(locals())
        return render.login(ctx)

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
            msg = u"username or password error"
            ctx = Storage(locals()) 
            return render.login(ctx)

class Logout:
    def GET(self):  
        web.ctx.session.kill()
        raise web.seeother("/index",absolute=True)

class Signup:
    def GET(self):
        session = web.ctx.session
        if session.get('loggedin',0) == 1:
            raise web.seeother("/index", absolute=True)
        ctx = Storage({'msg':None})
        return render.signup(ctx)

    def POST(self):
        session = web.ctx.session
        request = web.input()
        username = request.username
        password = request.password
        password_confirm = request.password_confirm
        if not username_re.match(username):
            msg = u"username is not valid, the length of it must >= 6 , and  it has to start with an alpha character"
            ctx = Storage(locals())
            return render.signup(ctx)
            
        if password != password_confirm:
            msg = u"password not equal to confirmed password"
            ctx = Storage(locals())
            return render.signup(ctx)
        email = request.email
        if not email_re.match(email):
            msg = u"Email not valid"
            ctx = Storage(locals())
            return render.signup(ctx)
        userid = get_userid(username)
        if userid == -1:
            newuser = User(password=password, username=username, email=email)
            #### whether email *UNIQUE* depends on the table in database you create
            try:
                newuser.save()
            except:
                msg = u"this email has been used"
                ctx = Storage(locals())
                return render.signup(ctx)
            newtenant = create_tenant(username)
            newtenant.add_user(get_keystoneuser_id(os_tenant_name), 
                                get_role_id('admin'))
            create_default_security_group_rules(username)
            floating_ip = create_floatingip(username)
        else:
            msg = u"username exists"
            ctx = Storage(locals())
            return render.signup(ctx)
        raise web.seeother("/login")

render_fluid = web.template.render('%s/templates/'%(mdir), base="fluid", globals=t_globals)

class Passwd:
    def GET(self):
        userid = web.ctx.session.get('userid',-1)
        superuser = is_superuser(userid)
        if userid == -1:
            raise web.seeother("/login")
        else:
            username = get_username(userid=userid)
            ctx = Storage(locals())
            return render_fluid.change_passwd(ctx)

    def POST(self):
        if web.ctx.session.get('loggedin',0) == 1:
            userid = web.ctx.session.get('userid',-1)
            superuser = is_superuser(userid)
            username = get_username(userid)
        request = web.input()
        old_password = request.old_password
        new_password = request.new_password
        new_password_confirm = request.new_password_confirm
        if new_password != new_password_confirm:
            msg = "Password doesn't match the confirmation"
            error = True
        elif len(new_password) < 6:
            msg = "Password too short"
            error = True
        else:
            user = User(username=username, password=old_password)
            if user.is_authenticated() == True:
                user.set_passwd(new_password)
                user.save(update=True)
                msg = "PassWord Changed"
                error = False
            else:
                msg = "Old PassWord Error"
                error = True
        ctx = Storage(locals())
        return render_fluid.change_passwd(ctx)

class Passwdcheck:
    def POST(self):
        web.header('Content-type','text/plain')
        if web.ctx.session.get('loggedin',0) == 1:
            userid = web.ctx.session.get('userid',-1)
            superuser = is_superuser(userid)
            username = get_username(userid)
        request = web.input()
        old_password = request.old_password
        user = User(username=username, password=old_password)
        if user.is_authenticated() == True:
            return 'ok'
        else:
            return 'fail'

class SSH:
    def GET(self):
        userid = web.ctx.session.get('userid',-1)
        superuser = is_superuser(userid)
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
        superuser = is_superuser(userid)
        if userid == -1:
            raise web.seeother('/index', absolute=True)
        username = get_username(userid=userid)

        request = web.input()
        ssh_key = request.ssh_key
        if ssh_key != '':
            if not (ssh_key.startswith("ssh-rsa") or ssh_key.startswith("ssh-dss")):
                msg = "SSH INPUT ERROR"
                error = True
                tenant_name = username
                keypair = fingerprint(tenant_name)
                ctx = Storage(locals())
                return render_fluid.ssh(ctx) 
            else:
                from uuid import uuid4
                temp_name = uuid4().hex
                try:
                    import_pubkey(temp_name, tenant_name=username ,pub_key=ssh_key)
                    delete_pubkey(temp_name, tenant_name=username) # Need to check again ?
                except:
                    ##the input ssh not validate
                    msg = "SSH INPUT ERROR"
                    error = True
                    tenant_name = username
                    keypair = fingerprint(tenant_name)
                    ctx = Storage(locals())
                    return render_fluid.ssh(ctx) 
                try:
                    delete_pubkey(username)
                except:
                    pass
                try:
                    import_pubkey(username,pub_key=ssh_key)
                except:
                    msg = "SSH INPUT ERROR"
                    error = True
                    tenant_name = username
                    keypair = fingerprint(tenant_name)
                    ctx = Storage(locals())
                    return render_fluid.ssh(ctx)
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
        superuser = is_superuser(userid)
        if userid == -1:
            raise web.seeother('/index', absolute=True)
        username = get_username(userid=userid)
        email = get_email(userid=userid) 
        ctx = Storage(locals())
        return render_fluid.email(ctx)
    
    def POST(self):
        userid = web.ctx.session.get('userid',-1)
        superuser = is_superuser(userid)
        if userid == -1:
            raise web.seeother('/index', absolute=True)
        username = get_username(userid=userid)
        request = web.input()
        email = request.email
        if email_re.match(email):
            update_email(userid, email)
            msg = "Email updated"
            error = False
            email = get_email(userid=userid) 
            ctx = Storage(locals())
            return render_fluid.email(ctx)
        else:
            msg = "Email not validate, using the old"
            error = True
            email = get_email(userid=userid) 
            ctx = Storage(locals())
            return render_fluid.email(ctx)

class Membercheck:
    def POST(self):
        web.header('Content-type','text/plain')
        request = web.input()
        username = request.username
        userid = get_userid(username)
        if userid == -1:
            return "ok"
        else:
            return "exist"

class Emailcheck:
    def POST(self):
        web.header('Content-type','text/plain')
        request = web.input()
        email = request.email
        userid = get_emailid(email)
        if userid == -1:
            return "ok"
        else:
            return "exist"

auth_app = web.application(urls, globals(), autoreload=True)
