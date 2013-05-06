A Manager for OpenStack
=======
I am not going to re-invent the wheel(Horizon), This is a (web.py + bootstrap)
based app for managing virtual machine for multi-user model ,some users are admins,
while the others are normal users,they need instances to do something.


Functions
========
to singed-up users, a user could apply a virtual machine, they if the admin 
admit his application,a virtual machine will be created for him, he then could 
login to his machine while SSH.and the applier could mange his own virtual machines,
while the admins could manage all the virtual machines.

ps: After signing up, a user have to supply a public key for ssh.


Install
========
If you are going to use sqlite3 as default database,below is a simple guide.
    
    $cd sql
    $sqlite ./db < schema.sql
    $cd ..
    $vi settings.conf
    $uwsgi ./uwsgi.ini

add a user as Administrator:

    $python
    Python 2.7.3 (default, May  3 2013, 22:48:14) 
    [GCC 4.6.3] on linux2
    Type "help", "copyright", "credits" or "license" for more information.
    >>> from auth import User
    >>> x = User(username="jj", password="123456", email="jj@yuzao.org", is_superuser=True)
    >>> x.save()

    

I am using nginx to deploy it:
        
    server {
        listen 8080;
        location /static {
            alias /home/jj/cm/static;
            autoindex on;
        }
        location / {
            uwsgi_pass  unix:///tmp/webpy_uwsgi.sock;
            include uwsgi_params;
        }
        rewrite ^/(.*)/$ /$1 permanent;
    }

***something maybe you should pay attention to,the admin role of openstack is "admin".***


Could you help me to improve it ?
========
Any Code help would be appreciated. thanks


***email***: jj@yuzao.org
