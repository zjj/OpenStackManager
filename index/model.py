import web
import ConfigParser

db_config = ConfigParser.ConfigParser()
db_config.read('settings.conf')
dbn = db_config.get('wiki_db','dbn')
database = db_config.get('wiki_db','db')
user = db_config.get('wiki_db','user')
pw = db_config.get('wiki_db','passwd')
table = db_config.get('wiki_db','table')
if dbn == 'sqlite':
    db = web.database(dbn=dbn, db=database)
if dbn == 'mysql':
    db = web.database(dbn=dbn, db=database, user=user, pw=pw)

def get_page():
    return db.select('wiki', order='id DESC')[0].ctx

def update_index_page(ctx):
    return db.insert('wiki', **locals())
