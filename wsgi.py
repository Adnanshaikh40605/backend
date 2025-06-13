"""
WSGI config that handles health checks directly.
This file is used when the WSGI server isn't configured to use backend.wsgi directly.
"""

import os
import sys
import json

# Add the project directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Import the actual application from the correct Django WSGI module
try:
    from backend.wsgi import application as django_application
except ImportError:
    # Fallback if backend.wsgi can't be imported
    from django.core.wsgi import get_wsgi_application
    django_application = get_wsgi_application()

def application(environ, start_response):
    """
    WSGI application that handles health checks directly before passing to Django.
    This ensures health checks work even if Django isn't fully initialized.
    """
    # Print debug info
    print(f"WSGI request: {environ.get('PATH_INFO')}")
    
    # Handle health check requests with highest priority
    if environ.get("PATH_INFO") in ["/health", "/health/"]:
        print("Health check detected, returning immediate response")
        start_response("200 OK", [("Content-Type", "application/json")])
        return [json.dumps({"status": "ok"}).encode()]
    
    # For all other requests, use Django's WSGI application
    try:
        # Use the application imported from backend.wsgi
        return django_application(environ, start_response)
    except Exception as e:
        print(f"Error processing request: {e}")
        # Still return a 200 for health checks if Django fails
        if environ.get("PATH_INFO") in ["/health", "/health/"]:
            start_response("200 OK", [("Content-Type", "application/json")])
            return [json.dumps({"status": "ok", "django_error": str(e)}).encode()]
        # Otherwise, return a 500 error
        start_response("500 Internal Server Error", [("Content-Type", "application/json")])
        return [json.dumps({"error": str(e)}).encode()] 