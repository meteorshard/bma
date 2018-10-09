# -*- coding: utf-8 -*-

import os

bind = '127.0.0.1:8080'
workers = 4 #worker测试
backlog = 2048
debug = True
proc_name = 'gunicorn.pid'
pidfile='/var/log/gunicorn/debug.log'
accesslog = '/tmp/log/gunicorn/access.log'
errorlog = '/tmp/log/gunicorn/error.log'
stdout_logfile = '/tmp/log/gunicorn/stdout.log'
stderr_logfile = '/tmp/log/gunicorn/stderr.log'
loglevel = 'debug'
