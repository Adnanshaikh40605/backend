"""
WSGI config for backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys
import traceback

print("Initializing WSGI application...")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

try:
    from django.core.wsgi import get_wsgi_application
    print("Successfully imported django.core.wsgi.get_wsgi_application")
    
    application = get_wsgi_application()
    print("WSGI application initialized successfully")
    
except Exception as e:
    print(f"Error initializing WSGI application: {e}")
    print(traceback.format_exc())
    
    # Create a simple WSGI application for debugging
    def debug_application(environ, start_response):
        status = '500 Internal Server Error'
        output = f"""
        <html>
        <head><title>Django Error</title></head>
        <body>
            <h1>Error initializing Django application</h1>
            <pre>{traceback.format_exc()}</pre>
        </body>
        </html>
        """.encode('utf-8')
        
        response_headers = [('Content-type', 'text/html'),
                          ('Content-Length', str(len(output)))]
        start_response(status, response_headers)
        return [output]
    
    application = debug_application
