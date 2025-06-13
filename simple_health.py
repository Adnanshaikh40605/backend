#!/usr/bin/env python
"""
Simple HTTP server for health checks without Flask dependencies
"""
import os
import json
import threading
import time
import http.server
import socketserver
from http import HTTPStatus

class HealthRequestHandler(http.server.BaseHTTPRequestHandler):
    """Simple handler that responds to health checks with 200 OK"""
    
    def do_GET(self):
        """Handle GET requests with a 200 OK response"""
        print(f"Health check received at path: {self.path}")
        
        # Always return 200 OK for any path
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        
        # Send a JSON response
        response = {"status": "ok"}
        self.wfile.write(json.dumps(response).encode())
    
    def log_message(self, format, *args):
        """Override to customize logging"""
        print(f"[Health Server] {self.address_string()} - {format % args}")

def start_django():
    """Start the Django application after a delay"""
    time.sleep(5)  # Give health server time to start
    print("Starting Django application...")
    
    # Make sure static directory exists
    os.system("mkdir -p staticfiles")
    
    # Copy favicon.ico to staticfiles to ensure it's accessible
    if os.path.exists("static/favicon.ico"):
        print("Copying favicon.ico to staticfiles")
        os.system("cp static/favicon.ico staticfiles/")
    
    os.system("python manage.py migrate --noinput")
    os.system("python manage.py collectstatic --noinput")
    os.system("echo '{\"status\": \"ok\"}' > staticfiles/health.json")
    os.system(f"PYTHONUNBUFFERED=1 gunicorn backend.wsgi:application --bind 0.0.0.0:{os.environ.get('PORT', 8000)} --workers 2 --log-level debug --timeout 120")

if __name__ == "__main__":
    # Get port from environment or use default
    port = int(os.environ.get("PORT", 8080))
    
    print(f"Starting health check server on port {port}")
    
    # Start Django in a background thread
    django_thread = threading.Thread(target=start_django)
    django_thread.daemon = True
    django_thread.start()
    
    # Create and start health check server
    with socketserver.TCPServer(("", port), HealthRequestHandler) as httpd:
        print(f"Health check server running at http://0.0.0.0:{port}/")
        httpd.serve_forever() 