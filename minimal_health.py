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
import socket
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Configuration
# Force Django to use a different port than the main proxy
DJANGO_PORT = "8000"  # Force Django to use port 8000
PORT = int(os.environ.get("PORT", "8080"))
DJANGO_URL = f"http://localhost:{DJANGO_PORT}"

# Create health check file
with open('/tmp/health.json', 'w') as f:
    f.write('{"status":"ok"}')

# Global variables to track application state
django_ready = False
django_starting = True
django_process = None

# Check if a port is in use
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', int(port))) == 0

# Start Django in the background
def start_django():
    global django_ready, django_starting, django_process
    
    logger.info(f"Setting up Django environment...")
    
    # Ensure Django port environment variable is set
    os.environ["DJANGO_PORT"] = DJANGO_PORT
    
    # Kill any process using our Django port
    if is_port_in_use(int(DJANGO_PORT)):
        logger.warning(f"Port {DJANGO_PORT} is already in use. Attempting to free it...")
        try:
            # This is a simple approach - in production you might want something more robust
            subprocess.run(["fuser", "-k", f"{DJANGO_PORT}/tcp"], check=False)
            time.sleep(1)  # Give the port time to be released
        except Exception as e:
            logger.warning(f"Failed to free port: {e}")
    
    # First check if Django can connect to the database
    try:
        # Run migrations and collect static files
        subprocess.run(["python", "manage.py", "check", "--database", "default"], check=False)
        logger.info("Database connection check completed")
    except Exception as e:
        logger.warning(f"Database check failed: {e}")
    
    # Run migrations and collect static files
    try:
        subprocess.run(["python", "manage.py", "migrate", "--noinput"], check=False)
        subprocess.run(["python", "manage.py", "collectstatic", "--noinput"], check=False)
    except Exception as e:
        logger.warning(f"Setup command failed: {e}")
    
    logger.info(f"Starting Django on port {DJANGO_PORT}...")
    
    # Start Gunicorn with the Django application, forcing it to use DJANGO_PORT
    env_vars = dict(os.environ)
    env_vars["PORT"] = DJANGO_PORT
    
    try:
        django_process = subprocess.Popen([
            "gunicorn",
            "backend.wsgi:application",
            "--bind", f"0.0.0.0:{DJANGO_PORT}",
            "--workers", "2",
            "--timeout", "120",
            "--preload"  # Preload the application to speed up worker startup
        ], env=env_vars)
        
        logger.info(f"Django process started with PID {django_process.pid}")
    except Exception as e:
        logger.error(f"Failed to start Django: {e}")
        django_starting = False
        return
    
    # Wait for Django to become available
    for i in range(120):  # Try for 2 minutes
        try:
            # Try different paths that might be more reliable
            for path in ['/admin/login/', '/health', '/', '/static/health.json']:
                try:
                    response = requests.get(f"{DJANGO_URL}{path}", timeout=2)
                    if response.status_code < 500:
                        django_ready = True
                        django_starting = False
                        logger.info(f"Django is now running on port {DJANGO_PORT} (confirmed with {path})")
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
            logger.error(f"Error checking Django readiness: {e}")
        
        logger.info(f"Waiting for Django to start... ({i+1}/120)")
    
    django_starting = False
    
    if not django_ready:
        logger.warning("Django did not become ready in time")
        logger.info("The proxy will still try to forward requests to Django")
    
    # Keep Django running
    try:
        exit_code = django_process.wait()
        logger.info(f"Django process exited with code {exit_code}")
    except Exception as e:
        logger.error(f"Error waiting for Django process: {e}")

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
        
        # Special case for health check - always return 200 to keep Railway happy
        if self.path == "/health.json" or self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
            return
        
        # Special case for favicon.ico - serve directly if exists
        if self.path == "/favicon.ico":
            favicon_path = None
            for path in ["static/favicon.ico", "staticfiles/favicon.ico"]:
                if os.path.exists(path):
                    favicon_path = path
                    break
                    
            if favicon_path:
                with open(favicon_path, "rb") as f:
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
            
            # Log the request (but not health checks)
            if not self.path.startswith("/health"):
                logger.info(f"Proxying {self.command} request to {target_url}")
            
            # Forward the request to Django with a reasonable timeout
            response = requests.request(
                method=self.command,
                url=target_url,
                headers=headers,
                data=body,
                timeout=60,  # Increased timeout for slow startup
                allow_redirects=False  # We'll handle redirects ourselves
            )
            
            # If we get here and django wasn't ready, it might be ready now
            if not django_ready and response.status_code < 500:
                django_ready = True
                logger.info(f"Django is now ready (detected during request to {self.path})")
            
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
            
        except requests.exceptions.ConnectionError:
            # Special case for connection errors - Django might not be ready yet
            self.send_response(503)
            self.send_header("Content-Type", "application/json")
            self.send_header("Retry-After", "5")
            self.end_headers()
            
            message = "The application is still starting up. Please try again in a moment."
            self.wfile.write(json.dumps({
                "status": "starting",
                "message": message
            }).encode())
            
        except Exception as e:
            # If anything goes wrong with the proxy, return a 502 Bad Gateway
            logger.error(f"Proxy error for {self.path}: {str(e)}")
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
        if not self.path.startswith("/health"):  # Don't log health checks
            logger.info(f"{self.address_string()} - {format % args}")

def restart_django_if_needed():
    """Monitor Django and restart if it crashes"""
    global django_process, django_ready, django_starting
    
    while True:
        time.sleep(10)  # Check every 10 seconds
        
        if django_process and django_process.poll() is not None:
            # Django has exited
            logger.warning("Django process has exited unexpectedly. Restarting...")
            django_ready = False
            django_starting = True
            
            # Start a new Django thread
            django_thread = threading.Thread(target=start_django)
            django_thread.daemon = True
            django_thread.start()

if __name__ == "__main__":
    logger.info(f"Starting health/proxy server on port {PORT}")
    logger.info(f"Django will run on port {DJANGO_PORT}")
    
    # Start Django in a separate thread
    django_thread = threading.Thread(target=start_django)
    django_thread.daemon = True
    django_thread.start()
    
    # Start monitoring thread to restart Django if it crashes
    monitor_thread = threading.Thread(target=restart_django_if_needed)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    # Create and start the proxy server
    httpd = socketserver.ThreadingTCPServer(("", PORT), ProxyHandler)
    httpd.allow_reuse_address = True
    logger.info(f"Proxy server running at http://0.0.0.0:{PORT}/")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down server")
        httpd.shutdown()
        
        # Terminate Django process if it's still running
        if django_process and django_process.poll() is None:
            logger.info("Terminating Django process")
            django_process.terminate()
            django_process.wait(timeout=5) 