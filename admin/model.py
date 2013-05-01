import web
import ConfigParser

db_config = ConfigParser.ConfigParser()
db_config.read('settings.conf')
dbn = db_config.get('server_db','dbn')
database = db_config.get('server_db','db')
user = db_config.get('server_db','user')
pw = db_config.get('server_db','passwd')
table = db_config.get('server_db','table')
if dbn == 'sqlite':
    db = web.database(dbn=dbn, db=database)
if dbn == 'mysql':
    db = web.database(dbn=dbn, db=database, user=user, pw=pw)

def get_all_pending_servers(userid=None):
    if userid == None:
        return db.select('server', order='user')
