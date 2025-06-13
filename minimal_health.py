#!/usr/bin/env python
"""
Ultra minimal health check server
"""
import os
import sys
import threading
import time
import http.server
import socketserver

# Create health check directory and file
os.makedirs('/tmp/health', exist_ok=True)
with open('/tmp/health/health.json', 'w') as f:
    f.write('{"status":"ok"}')

# Define a simple handler that serves the health.json file
class HealthHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory='/tmp/health', **kwargs)
    
    def log_message(self, format, *args):
        """Silence logging to avoid cluttering the output"""
        pass

def start_django():
    """Start Django after a delay"""
    time.sleep(5)
    print("Starting Django application...")
    os.system("python manage.py migrate --noinput")
    os.system("python manage.py collectstatic --noinput")
    
    # Use DJANGO_PORT for Django, separate from the health check server
    django_port = os.environ.get('DJANGO_PORT', 8000)
    print(f"Starting Django on port {django_port}")
    os.system(f"gunicorn backend.wsgi:application --bind 0.0.0.0:{django_port} --workers 2 --log-level debug --timeout 120")

if __name__ == '__main__':
    # Get port from environment or use default 
    health_port = int(os.environ.get('PORT', 8080))
    
    print(f"Starting health server on port {health_port}")
    
    # Start Django in a separate thread
    django_thread = threading.Thread(target=start_django)
    django_thread.daemon = True
    django_thread.start()
    
    # Run the health server
    with socketserver.TCPServer(("", health_port), HealthHandler) as httpd:
        print(f"Health server running on port {health_port}")
        httpd.serve_forever() 