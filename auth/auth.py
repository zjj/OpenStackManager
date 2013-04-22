import random
import hashlib
import ConfigParser
import web

db_config = ConfigParser.ConfigParser()
db_config.read('settings.conf')
dbn = db_config.get('user_db','dbn')
database = db_config.get('user_db','db')
user = db_config.get('user_db','user')
pw = db_config.get('user_db','passwd')
table = db_config.get('user_db','table')
if dbn == 'sqlite':
    db = web.database(dbn=dbn, db=database)
if dbn == 'mysql':
    db = web.database(dbn=dbn, db=database, user=user, pw=pw)

class User:
    def __init__(self,  password=None, username=None, **more):
        self.username = username     
        self.salt = self._generate_salt()
        self.password = self._generate_passwd(self.salt, password)
        self.encrypt_passwd = self.salt + '$' + self.password
        self.more = more
        self.__dict__.update(more)

    def _generate_salt(self):
        salt_set = ('abcdefghijklmnopqrstuvwxyz'
                    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                    '0123456789./')
        salt = range(0,16) 
        return ''.join([random.choice(salt_set) for c in salt])

    def _generate_passwd(self, salt=None, passwd=None):
        return hashlib.sha1(salt+passwd).hexdigest()

    def set_passwd(self, passwd):
        pass    

    def save(self):
        db.insert(table, username=self.username, password=self.encrypt_passwd, **self.more)

    def is_authenticated(self):
        pass

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




