"""
WSGI config for SkillMatchHub project.
"""

import os

# Use PyMySQL as MySQLdb
import pymysql
pymysql.install_as_MySQLdb()

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()
