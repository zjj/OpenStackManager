import ConfigParser
import web

db_config = ConfigParser.ConfigParser()
db_config.read('settings.conf')
dbn = db_config.get('db','dbn')
database = db_config.get('db','db')
host = db_config.get('db', 'host')
port =int(db_config.get('db','port'))
user = db_config.get('db','user')
pw = db_config.get('db','passwd')
user_table = db_config.get('db','user_table')
wiki_table = db_config.get('db','wiki_table')
server_table = db_config.get('db','server_table')


if dbn == 'sqlite':
    db = web.database(dbn=dbn, db=database)
if dbn == 'mysql':
    db = web.database(dbn=dbn, host=host, port=port, db=database, user=user, pw=pw)
