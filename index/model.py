import web
import ConfigParser
from db import db

def get_page():
    return db.select('wiki', order='id DESC')[0].ctx

def update_index_page(ctx):
    return db.insert('wiki', **locals())
