"""
WSGI config that handles health checks directly.
"""

import os
import sys

# Add the project directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

def application(environ, start_response):
    """
    WSGI application that handles health checks directly before passing to Django.
    This ensures health checks work even if Django isn't fully initialized.
    """
    # Intercept health check requests
    if environ.get("PATH_INFO") in ["/health", "/health/"]:
        start_response("200 OK", [("Content-Type", "application/json")])
        return [b'{"status": "ok"}']
    
    # For all other requests, use Django's WSGI application
    from django.core.wsgi import get_wsgi_application
    return get_wsgi_application()(environ, start_response) 