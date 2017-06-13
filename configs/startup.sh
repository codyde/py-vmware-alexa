#!/bin/sh

NGINX=/usr/sbin/nginx
WEB=/usr/sbin/uwsgi

$NGINX && $WEB --ini /etc/uwsgi.d/avss.ini

