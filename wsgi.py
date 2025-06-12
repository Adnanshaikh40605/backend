"""
WSGI config for backend project.
"""

import os
import sys

# Add the project directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Import Django's WSGI application
from django.core.wsgi import get_wsgi_application

# Create the WSGI application
application = get_wsgi_application()

# Add a simple health check handler
def health_check(environ, start_response):
    status = '200 OK'
    headers = [('Content-type', 'application/json')]
    start_response(status, headers)
    return [b'{"status": "ok"}']

# Wrap the WSGI application to handle health checks
def application_with_health_check(environ, start_response):
    path_info = environ.get('PATH_INFO', '')
    if path_info == '/health' or path_info == '/health/':
        return health_check(environ, start_response)
    return application(environ, start_response)

# Use the wrapped application
application = application_with_health_check 