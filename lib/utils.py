import web

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

def login_required(f):
    def wrap(*args, **kwargs):
        userid = web.ctx.session.get('userid',-1)
        if userid ==  -1:
            raise web.seeother("/auth/login", absolute=True)
        return f(*args, **kwargs)
    return wrap
