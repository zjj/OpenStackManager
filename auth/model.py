import re
import random
import hashlib
import ConfigParser
import web
from db import db
from db import user_table as table

class User:
    def __init__(self, username=None, password=None, **opts):
        self.username = username
        self.raw_passwd = password
        self.salt = self._generate_salt()
        self.password = self._generate_passwd(self.salt, password)
        self.encrypt_passwd = self.salt + '$' + self.password
        self.opts = opts
        self.__dict__.update(opts)

    def _generate_salt(self):
        salt_set = ('abcdefghijklmnopqrstuvwxyz'
                    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                    '0123456789./')
        salt = range(0,16) 
        return ''.join([random.choice(salt_set) for c in salt])

    def _generate_passwd(self, salt=None, passwd=None):
        return hashlib.sha1(salt+passwd).hexdigest()

    def set_passwd(self, passwd):
        self.salt = self._generate_salt()
        self.encrypt_passwd = self.salt + '$' + self._generate_passwd(self.salt, passwd)

    def save(self,update=False):
        if update == False:
            db.insert(table, username=self.username, password=self.encrypt_passwd, **self.opts)
        else:
            db.update(table, where="username=$username", vars={'username':self.username}, password=self.encrypt_passwd, **self.opts)    

    def is_authenticated(self):
        return authenticate(passwd=self.raw_passwd, username=self.username)


def authenticate(passwd=None, username=None):
    user = db.select(table,what='password', where='username=$username',vars={'username':username})
    user = user.list()
    if len(user) == 0:
        return False
    else:
        encrypt_passwd = user[0].password
        split = encrypt_passwd.split('$')
        salt = split[0]
        if hashlib.sha1(salt+passwd).hexdigest() == split[1]:
            return True
        else:
            return False

def get_userid(username=None):
    try:
        return db.select(table,what='id', where='username=$username',vars={'username':username})[0].id
    except:
        return -1

def get_username(userid=None):
    try:
        return db.select(table,what='username', where='id=$userid',vars={'userid':userid})[0].username
    except:
        return None

def get_email(userid=None):
    try:
        return db.select(table,what='email', where='id=$userid',vars={'userid':userid})[0].email
    except:
        return None

def is_superuser(userid=None):
    try:
        return True if db.select(table,what='is_superuser', where='id=$userid',vars={'userid':userid})[0].is_superuser else False
    except:
        return False


#TO BE IMPROVED, i think this should in class User
def update_email(userid, email):
    try:
        return db.update(table, where="id=$userid", vars={'userid':userid}, email=email)  
    except:
        return None

email_re = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*" 
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"'
    r')@((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)$)' 
    r'|\[(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\]$', re.IGNORECASE)


username_re = re.compile(r'^[a-zA-Z]\w{5,19}$')


