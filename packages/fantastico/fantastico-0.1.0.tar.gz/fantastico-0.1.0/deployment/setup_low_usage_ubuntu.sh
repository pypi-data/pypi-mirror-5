#!/bin/bash
PATH=/usr/bin:/usr/sbin

echo $ROOT_PASSWD | sudo -S apt-get install nginx -y

. ../pip-deps/bin/activate

export PYTHONPATH=`pwd`/../

python3 ../fantastico/deployment/config_nginx.py $@ >> fantastico-framework.com.conf

echo $ROOT_PASSWD | sudo -S mv fantastico-framework.com.conf /etc/nginx/sites-available/fantastico-framework.com.conf
echo $ROOT_PASSWD | sudo -S ln -fs /etc/nginx/sites-available/fantastico-framework.com.conf /etc/nginx/sites-enabled/fantastico-framework.com.conf
echo $ROOT_PASSWD | sudo -S service nginx restart