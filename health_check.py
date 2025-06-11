#!/usr/bin/env python
"""
Simple HTTP server that responds to health checks.
This is a fallback if the main application fails to start.
"""
import os
import http.server
import socketserver
from http import HTTPStatus

class HealthHandler(http.server.SimpleHTTPRequestHandler):
    """Handler for health check requests."""
    
    def do_GET(self):
        """Handle GET requests."""
        print(f"Received request for path: {self.path}")
        if self.path == '/health/' or self.path == '/health':
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "ok", "message": "Health check OK (fallback server)"}')
            print("Health check request responded with OK")
        else:
            self.send_response(HTTPStatus.NOT_FOUND)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not Found')
            print(f"Request for {self.path} responded with 404")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f"Starting fallback health check server on port {port}...")
    print(f"PORT environment variable: '{os.environ.get('PORT', 'Not set')}'")
    
    # Use the handler class with ThreadingTCPServer for better performance
    with socketserver.ThreadingTCPServer(("", port), HealthHandler) as httpd:
        print(f"Serving health check at http://0.0.0.0:{port}/health/")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Server stopped by user")
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            httpd.server_close()
            print("Server closed") 