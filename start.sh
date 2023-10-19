#!/bin/bash

cd /home
useradd -s /sbin/nologin -M nginx

flask run -h :: -p 10004 &

/usr/local/nginx/sbin/nginx -g 'daemon off;'
