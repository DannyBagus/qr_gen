"""
WSGI config for qr_gen_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

# Default auf prod, falls nichts angegeben wird (sicherer)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qr_gen_project.settings.prod')

application = get_wsgi_application()