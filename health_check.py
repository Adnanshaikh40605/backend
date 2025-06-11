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
        if self.path == '/health/' or self.path == '/health':
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(b'{"status": "ok", "message": "Health check OK"}')
        else:
            self.send_response(HTTPStatus.NOT_FOUND)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'Not Found')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f"Starting health check server on port {port}...")
    
    with socketserver.TCPServer(("", port), HealthHandler) as httpd:
        print(f"Serving health check at http://0.0.0.0:{port}/health/")
        httpd.serve_forever() 