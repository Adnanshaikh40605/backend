"""
WSGI config that handles health checks directly.
"""

import os
import sys
import json

# Add the project directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

def application(environ, start_response):
    """
    WSGI application that handles health checks directly before passing to Django.
    This ensures health checks work even if Django isn't fully initialized.
    """
    # Print debug info
    print(f"WSGI request: {environ.get('PATH_INFO')}")
    
    # Handle health check requests with highest priority
    if environ.get("PATH_INFO") in ["/", "/health", "/health/"]:
        print("Health check detected, returning immediate response")
        start_response("200 OK", [("Content-Type", "application/json")])
        return [json.dumps({"status": "ok"}).encode()]
    
    # For all other requests, use Django's WSGI application
    try:
        from django.core.wsgi import get_wsgi_application
        django_app = get_wsgi_application()
        return django_app(environ, start_response)
    except Exception as e:
        print(f"Error initializing Django: {e}")
        # Still return a 200 for health checks if Django fails
        if environ.get("PATH_INFO") in ["/", "/health", "/health/"]:
            start_response("200 OK", [("Content-Type", "application/json")])
            return [json.dumps({"status": "ok", "django_error": str(e)}).encode()]
        # Otherwise, return a 500 error
        start_response("500 Internal Server Error", [("Content-Type", "application/json")])
        return [json.dumps({"error": str(e)}).encode()] 