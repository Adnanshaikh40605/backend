#!/usr/bin/env python
"""
Health check server with robust reverse proxy to Django
"""
import http.server
import socketserver
import os
import subprocess
import threading
import time
import json
import requests
from urllib.parse import urlparse

# Configuration
DJANGO_PORT = os.environ.get("DJANGO_PORT", "8000")
PORT = int(os.environ.get("PORT", "8080"))
DJANGO_URL = f"http://localhost:{DJANGO_PORT}"

# Create health check file
with open('/tmp/health.json', 'w') as f:
    f.write('{"status":"ok"}')

# Global variable to track if Django is running
django_ready = False

# Start Django in the background
def start_django():
    global django_ready
    
    print(f"Setting up Django environment...")
    
    # First check if Django can connect to the database
    try:
        # Run migrations and collect static files
        subprocess.run(["python", "manage.py", "check", "--database", "default"], check=False)
        print("Database connection check completed")
    except Exception as e:
        print(f"Warning: Database check failed: {e}")
    
    # Run migrations and collect static files
    subprocess.run(["python", "manage.py", "migrate", "--noinput"], check=False)
    subprocess.run(["python", "manage.py", "collectstatic", "--noinput"], check=False)
    
    print(f"Starting Django on port {DJANGO_PORT}...")
    
    # Start Gunicorn with the Django application
    process = subprocess.Popen([
        "gunicorn",
        "backend.wsgi:application",
        "--bind", f"0.0.0.0:{DJANGO_PORT}",
        "--workers", "2",
        "--timeout", "120",
        "--preload"  # Preload the application to speed up worker startup
    ])
    
    # Wait for Django to become available
    for i in range(60):  # Try for 60 seconds instead of 30
        try:
            # Try different paths that might be more reliable
            for path in ['/admin/login/', '/health', '/', '/static/health.json']:
                try:
                    response = requests.get(f"{DJANGO_URL}{path}", timeout=2)
                    if response.status_code < 500:
                        django_ready = True
                        print(f"Django is now running on port {DJANGO_PORT} (confirmed with {path})")
                        break
                except requests.RequestException:
                    continue
            
            if django_ready:
                break
        except Exception as e:
            print(f"Error checking Django readiness: {e}")
        
        print(f"Waiting for Django to start... ({i+1}/60)")
        time.sleep(1)
    
    if not django_ready:
        print("WARNING: Django did not become ready in time")
    
    # Keep Django running
    process.wait()

# Health check + Reverse Proxy handler
class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request()
    
    def do_POST(self):
        self.handle_request()
    
    def do_PUT(self):
        self.handle_request()
    
    def do_DELETE(self):
        self.handle_request()
    
    def do_OPTIONS(self):
        self.handle_request()
    
    def handle_request(self):
        # Special case for health check
        if self.path == "/health.json":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
            return
        
        # Special case for favicon.ico - serve directly if exists
        if self.path == "/favicon.ico" and os.path.exists("static/favicon.ico"):
            with open("static/favicon.ico", "rb") as f:
                self.send_response(200)
                self.send_header("Content-Type", "image/x-icon")
                self.end_headers()
                self.wfile.write(f.read())
            return
            
        # Special case for root path - always return something useful
        if self.path == "/" and not django_ready:
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            status_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Blog CMS API</title>
                <meta http-equiv="refresh" content="5">
                <style>
                    body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; padding: 20px; }}
                    h1 {{ color: #2C3E50; }}
                    .card {{ border: 1px solid #ddd; border-radius: 4px; padding: 15px; background-color: #f9f9f9; }}
                    .status {{ color: #e67e22; font-weight: bold; }}
                </style>
            </head>
            <body>
                <h1>Blog CMS API</h1>
                <div class="card">
                    <p><span class="status">Starting up...</span> The application is initializing.</p>
                    <p>This page will refresh automatically every 5 seconds.</p>
                    <p>The Django application is currently starting. Please wait a moment.</p>
                </div>
            </body>
            </html>
            """
            self.wfile.write(status_html.encode())
            return
        
        # If Django is not ready, return a friendly message
        if not django_ready:
            self.send_response(503)
            self.send_header("Content-Type", "application/json")
            self.send_header("Retry-After", "10")
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "starting",
                "message": "Application is starting, please try again in a moment"
            }).encode())
            return
        
        # Forward request to Django
        try:
            # Get request body if present
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None
            
            # Prepare headers for the proxied request
            headers = {}
            for key, value in self.headers.items():
                if key.lower() not in ('host', 'content-length'):
                    headers[key] = value
            
            # Preserve original URL path and query string
            url_parts = urlparse(self.path)
            target_url = f"{DJANGO_URL}{url_parts.path}"
            if url_parts.query:
                target_url += f"?{url_parts.query}"
            
            # Forward the request to Django
            response = requests.request(
                method=self.command,
                url=target_url,
                headers=headers,
                data=body,
                timeout=30,
                allow_redirects=False  # We'll handle redirects ourselves
            )
            
            # Forward Django's response back to the client
            self.send_response(response.status_code)
            
            # Forward headers from Django, but skip some problematic ones
            skip_headers = ('transfer-encoding', 'connection', 'keep-alive')
            for key, value in response.headers.items():
                if key.lower() not in skip_headers:
                    self.send_header(key, value)
            
            self.end_headers()
            
            # Forward response body
            self.wfile.write(response.content)
            
        except Exception as e:
            # If anything goes wrong with the proxy, return a 502 Bad Gateway
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "error",
                "message": f"Proxy error: {str(e)}"
            }).encode())
    
    def log_message(self, format, *args):
        if self.path != "/health.json":  # Don't log health checks
            print(f"{self.address_string()} - {format % args}")

if __name__ == "__main__":
    print(f"Starting health/proxy server on port {PORT}")
    
    # Start Django in a separate thread
    django_thread = threading.Thread(target=start_django)
    django_thread.daemon = True
    django_thread.start()
    
    # Create and start the proxy server
    httpd = socketserver.ThreadingTCPServer(("", PORT), ProxyHandler)
    print(f"Proxy server running at http://0.0.0.0:{PORT}/")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down server")
        httpd.shutdown() 