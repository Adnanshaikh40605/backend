#!/usr/bin/env python
"""
Ultra minimal health check server with proxy capabilities
"""
import os
import sys
import threading
import time
import http.server
import socketserver
import urllib.request
import urllib.error
import socket

# Create health check directory and file
os.makedirs('/tmp/health', exist_ok=True)
with open('/tmp/health/health.json', 'w') as f:
    f.write('{"status":"ok"}')

# Flag to track if Django is ready
django_ready = False
django_port = int(os.environ.get('DJANGO_PORT', 8000))

# Define a handler that serves health checks and proxies other requests to Django
class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        # Serve health checks directly
        if self.path == '/health.json':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status":"ok"}')
            return
            
        # Try to proxy to Django if it's ready
        global django_ready
        if django_ready:
            try:
                # Try to forward the request to Django
                url = f"http://localhost:{django_port}{self.path}"
                req = urllib.request.Request(url, headers=dict(self.headers))
                with urllib.request.urlopen(req, timeout=5) as response:
                    # Copy response status and headers
                    self.send_response(response.status)
                    for header, value in response.getheaders():
                        self.send_header(header, value)
                    self.end_headers()
                    # Copy response body
                    self.wfile.write(response.read())
                return
            except (urllib.error.URLError, socket.timeout) as e:
                print(f"Error proxying to Django: {e}")
                # Fall through to 502 response
        
        # Django is not ready or proxy failed, return 502
        self.send_response(502)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(b'{"error":"Application starting, please try again in a moment"}')
    
    # Handle all HTTP methods the same way
    do_POST = do_GET
    do_PUT = do_GET
    do_DELETE = do_GET
    do_OPTIONS = do_GET
    
    def log_message(self, format, *args):
        """Only log errors to avoid cluttering the output"""
        if args[1][0] in ('4', '5'):  # Log 4xx and 5xx responses
            print(f"[Health Server] {self.address_string()} - {format % args}")

def start_django():
    """Start Django after a delay"""
    global django_ready
    
    time.sleep(5)
    print("Starting Django application...")
    os.system("python manage.py migrate --noinput")
    os.system("python manage.py collectstatic --noinput")
    
    # Use DJANGO_PORT for Django, separate from the health check server
    print(f"Starting Django on port {django_port}")
    
    # We need to use subprocess to keep track of when Django is ready
    import subprocess
    django_process = subprocess.Popen(
        f"gunicorn backend.wsgi:application --bind 0.0.0.0:{django_port} --workers 2 --log-level debug --timeout 120",
        shell=True
    )
    
    # Wait for Django to become ready by checking the port
    retry_count = 0
    while retry_count < 30:  # Try for about 30 seconds
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', django_port))
                if result == 0:
                    print(f"Django is now ready on port {django_port}")
                    django_ready = True
                    break
        except:
            pass
        retry_count += 1
        time.sleep(1)
    
    if not django_ready:
        print("WARNING: Django did not become ready in time")
    
    # Keep the Django process running
    django_process.wait()

if __name__ == '__main__':
    # Get port from environment or use default 
    health_port = int(os.environ.get('PORT', 8080))
    
    print(f"Starting health/proxy server on port {health_port}")
    print(f"Django will run on port {django_port}")
    
    # Start Django in a separate thread
    django_thread = threading.Thread(target=start_django)
    django_thread.daemon = True
    django_thread.start()
    
    # Run the health/proxy server
    with socketserver.TCPServer(("", health_port), ProxyHandler) as httpd:
        print(f"Health/proxy server running on port {health_port}")
        httpd.serve_forever() 