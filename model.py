import ConfigParser
import web

db_config = ConfigParser.ConfigParser()
db_config.read('settings.conf')
dbn = db_config.get('user_db','dbn')
database = db_config.get('user_db','db')
user = db_config.get('user_db','user')
pw = db_config.get('user_db','passwd')
if dbn == 'sqlite':
    db = web.database(dbn=dbn, db=database)
if dbn == 'mysql':
    db = web.database(dbn=dbn, db=database, user=user, pw=pw)

