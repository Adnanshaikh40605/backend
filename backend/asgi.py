"""
ASGI config for backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
import sys
import traceback

print("Initializing ASGI application...")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

try:
    application = get_asgi_application()
    print("ASGI application initialized successfully")
except Exception as e:
    print(f"Error initializing ASGI application: {e}")
    print(traceback.format_exc())
    
    # Create a simple ASGI application for debugging
    async def debug_application(scope, receive, send):
        if scope["type"] == "http":
            await send({
                "type": "http.response.start",
                "status": 500,
                "headers": [
                    [b"content-type", b"text/html"]
                ]
            })
            
            error_message = f"""
            <html>
            <head><title>Django Error</title></head>
            <body>
                <h1>Error initializing Django ASGI application</h1>
                <pre>{traceback.format_exc()}</pre>
            </body>
            </html>
            """.encode("utf-8")
            
            await send({
                "type": "http.response.body",
                "body": error_message
            })
    
    application = debug_application
