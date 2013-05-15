import web
import ConfigParser
import sys
from db import db

def get_all_pending_servers(userid=None):
    if userid == None:
        return db.select('server', order='user')

def delete_pending_server(id=None):
    return db.delete('server', where="id=$id", vars=locals())

def get_pending_server_info(id=None):
    return db.select('server', where="id=$id", vars=locals())
    
