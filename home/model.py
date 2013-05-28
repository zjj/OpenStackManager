import web
import ConfigParser
from db import db

def get_servers(userid=None):
    return db.select('server', where='user=$userid',vars=locals(), order='id DESC')

def add_server(user, server_name, image, flavor):
    return db.insert('server',**locals())

def delete_server(image=None):
    '''Delete a server by image_id'''
    return db.delete('server', where="image=$image", vars=locals())
