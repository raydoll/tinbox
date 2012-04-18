import os
import sys 

sys.path = ['/opt/webapps/{{domain}}/env','/opt/webapps/{{domain}}/env/{{project}}'] + sys.path

os.environ['DJANGO_SETTINGS_MODULE'] = '{{project}}.settings'

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
