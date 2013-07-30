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


nova_dbn=db_config.get('nova', 'dbn')
nova_db_host=db_config.get('nova', 'host')
nova_db_port=int(db_config.get('nova', 'port'))
nova_db_name=db_config.get('nova', 'db')
instance_table=db_config.get('nova', 'instance_table')
nova_db_user=db_config.get('nova', 'user')
nova_db_passwd=db_config.get('nova', 'passwd')

if nova_dbn == 'sqlite':
    nova_db = web.database(dbn=nova_dbn, db=nova_db_name)
if nova_dbn == 'mysql':
    nova_db = web.database(dbn=nova_dbn, host=nova_db_host, port=nova_db_port, db=nova_db_name, user=nova_db_user, pw=nova_db_passwd)


