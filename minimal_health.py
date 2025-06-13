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
# Force Django to use a different port than the main proxy
DJANGO_PORT = "8000"  # Force Django to use port 8000
PORT = int(os.environ.get("PORT", "8080"))
DJANGO_URL = f"http://localhost:{DJANGO_PORT}"

# Create health check file
with open('/tmp/health.json', 'w') as f:
    f.write('{"status":"ok"}')

# Global variable to track if Django is running
django_ready = False
django_starting = True

# Start Django in the background
def start_django():
    global django_ready, django_starting
    
    print(f"Setting up Django environment...")
    
    # Ensure Django port environment variable is set
    os.environ["DJANGO_PORT"] = DJANGO_PORT
    
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
    
    # Start Gunicorn with the Django application, forcing it to use DJANGO_PORT
    process = subprocess.Popen([
        "gunicorn",
        "backend.wsgi:application",
        "--bind", f"0.0.0.0:{DJANGO_PORT}",
        "--workers", "2",
        "--timeout", "120",
        "--preload"  # Preload the application to speed up worker startup
    ], env=dict(os.environ, PORT=DJANGO_PORT))
    
    # Wait for Django to become available
    for i in range(120):  # Try for 2 minutes now
        try:
            # Try different paths that might be more reliable
            for path in ['/admin/login/', '/health', '/', '/static/health.json']:
                try:
                    response = requests.get(f"{DJANGO_URL}{path}", timeout=2)
                    if response.status_code < 500:
                        django_ready = True
                        django_starting = False
                        print(f"Django is now running on port {DJANGO_PORT} (confirmed with {path})")
                        break
                except requests.RequestException:
                    continue
            
            if django_ready:
                break
                
            # Sleep less at the beginning to detect fast starts
            if i < 10:
                time.sleep(0.5)
            else:
                time.sleep(1)
                
        except Exception as e:
            print(f"Error checking Django readiness: {e}")
        
        print(f"Waiting for Django to start... ({i+1}/120)")
    
    django_starting = False
    
    if not django_ready:
        print("WARNING: Django did not become ready in time")
        print("The proxy will still try to forward requests to Django")
    
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
        global django_ready
        
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
        if self.path == "/" and django_starting:
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
                    .loader {{ 
                        border: 5px solid #f3f3f3;
                        border-top: 5px solid #3498db;
                        border-radius: 50%;
                        width: 30px;
                        height: 30px;
                        animation: spin 2s linear infinite;
                        margin: 20px auto;
                    }}
                    @keyframes spin {{
                        0% {{ transform: rotate(0deg); }}
                        100% {{ transform: rotate(360deg); }}
                    }}
                </style>
            </head>
            <body>
                <h1>Blog CMS API</h1>
                <div class="card">
                    <p><span class="status">Starting up...</span> The application is initializing.</p>
                    <div class="loader"></div>
                    <p>This page will refresh automatically every 5 seconds.</p>
                    <p>The Django application is currently starting. Please wait a moment.</p>
                </div>
            </body>
            </html>
            """
            self.wfile.write(status_html.encode())
            return
        
        # Try forwarding to Django even if not officially ready - it might work for some endpoints
        # This helps with startup when Django is partially ready
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
            
            # If we get here and django wasn't ready, it might be ready now
            if not django_ready and response.status_code < 500:
                django_ready = True
                print(f"Django is now ready (detected during request to {self.path})")
            
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
            
            # Different message based on django state
            if django_starting:
                message = "Application is still starting up. Please try again in a moment."
            else:
                message = f"Proxy error: {str(e)}"
                
            self.wfile.write(json.dumps({
                "status": "error",
                "message": message
            }).encode())
    
    def log_message(self, format, *args):
        if self.path != "/health.json":  # Don't log health checks
            print(f"{self.address_string()} - {format % args}")

if __name__ == "__main__":
    print(f"Starting health/proxy server on port {PORT}")
    print(f"Django will run on port {DJANGO_PORT}")
    
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