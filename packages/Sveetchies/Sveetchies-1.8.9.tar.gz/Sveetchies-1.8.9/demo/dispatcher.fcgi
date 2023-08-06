#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, os

# Add a custom Python path.
sys.path.insert(0, '/home/django/py_libs')
sys.path.insert(0, '/home/django/projects/Sveetchies/')

# Pour indiquer le chemin à utiliser pour stocker le cache des modules en Eggs
os.environ['PYTHON_EGG_CACHE'] = "/tmp"

# Set the DJANGO_SETTINGS_MODULE environment variable.
os.environ['DJANGO_SETTINGS_MODULE'] = "demo.prod_settings"

from django.core.servers.fastcgi import runfastcgi
runfastcgi(method="threaded", daemonize="false")
