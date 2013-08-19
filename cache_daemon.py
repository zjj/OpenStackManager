#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import json
from lib.fakeopenstack import *
from db import db


def update_cache():
    '''
    update the cache database
    '''
    all_servers = get_tenant_servers(tenant_name=os_tenant_name)
    server_detail = {}
    for s in all_servers:
        s_dict = s.__dict__
        s_dict.pop('manager')
        try:
            tenant_id = s_dict['tenant_id']
            server_detail[tenant_id].append(s_dict)
        except KeyError:
            server_detail[tenant_id] = [s_dict,]

    all_tenants = get_all_tenants()
    tenants_dict = dict([(t.id, t.name) for t in all_tenants])

    floatingips_dict={}
    for tenant_id, tenant_name in tenants_dict.items():
        floatingips = [f.ip for f in get_floatingips(tenant_name)]
        floatingips_dict.update({tenant_name: floatingips})

    flavors = get_flavors(os_tenant_name)
    flavors_dict = dict([(f.id,'cpus:%s ram:%s disk:%s'%(f.vcpus, f.ram, f.disk)) for f in flavors])

    images = get_images(os_tenant_name)
    images_dict = dict([(i.id, i.name) for i in images])

    for tenant, val in server_detail.items():
        for server in val:
            flavor_id = server['flavor']['id']
            server['flavor'].update({'desc': flavors_dict[flavor_id]})
            image_id = server['image']['id']
            server['image'].update({'name': images_dict[image_id]})
        server_detail.update({tenants_dict[tenant]:val})
        del server_detail[tenant]

    server_detail = json.dumps(server_detail)  #str
    images_dict = json.dumps(images_dict)  #str
    flavors_dict = json.dumps(flavors_dict)  #str
    floatingips_dict = json.dumps(floatingips_dict) #str

    db.update('cache', where='describle=$desc', vars={'desc':'servers'}, detail=server_detail)
    db.update('cache', where='describle=$desc', vars={'desc':'images'}, detail=images_dict)
    db.update('cache', where='describle=$desc', vars={'desc':'flavors'}, detail=flavors_dict)
    db.update('cache', where='describle=$desc', vars={'desc':'floatingips'}, detail=floatingips_dict)


if __name__ == '__main__':
    while True:
        update_cache()
        time.sleep(5)
