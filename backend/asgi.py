"""
ASGI config for backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
import sys
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("asgi")

# Log startup information
logger.info("Initializing ASGI application...")
logger.info(f"Python version: {sys.version}")
logger.info(f"Current directory: {os.getcwd()}")

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Get the ASGI application
application = get_asgi_application()
logger.info("ASGI application initialized successfully")
