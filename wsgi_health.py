"""
A WSGI application that integrates health checks with the Django application.
"""
import os
import sys
from django.core.wsgi import get_wsgi_application
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("wsgi_health")

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Get the Django WSGI application
django_application = get_wsgi_application()

def simple_health_app(environ, start_response):
    """A simple WSGI app that always returns 200 OK for health checks."""
    status = '200 OK'
    headers = [('Content-type', 'text/plain')]
    start_response(status, headers)
    return [b'OK']

def combined_application(environ, start_response):
    """
    A WSGI application that serves health checks at /railway-health/ and
    passes all other requests to the Django application.
    """
    path = environ.get('PATH_INFO', '')
    
    # Log all requests for debugging
    logger.info(f"Request received: {path} (Method: {environ.get('REQUEST_METHOD')})")
    
    # Health check endpoints
    if path == '/' or path == '/health' or path == '/health/' or path == '/railway-health/' or path == '/railway-health':
        logger.info(f"Health check request detected at {path}")
        return simple_health_app(environ, start_response)
    
    # All other requests go to Django
    return django_application(environ, start_response)

# The WSGI entry point
application = combined_application 