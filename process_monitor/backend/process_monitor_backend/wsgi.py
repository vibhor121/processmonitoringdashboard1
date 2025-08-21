"""
WSGI config for process_monitor_backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Use production settings if specified, otherwise fall back to default
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'process_monitor_backend.settings')

application = get_wsgi_application()
