"""
WSGI config for backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("wsgi")

# Log startup
logger.info("Initializing WSGI application...")

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
logger.info("WSGI application initialized successfully")
