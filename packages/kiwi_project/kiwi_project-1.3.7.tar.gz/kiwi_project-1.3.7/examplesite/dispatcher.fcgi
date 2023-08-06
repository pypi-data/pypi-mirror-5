#!/usr/bin/python
import sys, os

# Add a custom Python path.
sys.path.insert(0, '/home/django/Apps/Django')
sys.path.insert(0, '/home/django/py_libs')
sys.path.insert(0, '/home/django/projects/kiwi_project/')

# Set the DJANGO_SETTINGS_MODULE environment variable.
os.environ['DJANGO_SETTINGS_MODULE'] = "examplesite.prod_settings"

from django.core.servers.fastcgi import runfastcgi
runfastcgi(method="threaded", daemonize="false")
