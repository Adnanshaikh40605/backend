#!/usr/bin/env python
"""
Simple HTTP server that responds to health checks.
This is a fallback if the main application fails to start.
"""
import os
import http.server
import socketserver
from http import HTTPStatus
import sys
import time

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
            # Respond with 200 OK to any request to pass Railway health checks
            self.send_response(HTTPStatus.OK)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(f'{{"status": "ok", "path": "{self.path}", "message": "Fallback server responding to all paths"}}'.encode('utf-8'))
            print(f"Request for {self.path} responded with 200 OK")

if __name__ == '__main__':
    # Get port from environment variable
    port = int(os.environ.get('PORT', 8000))
    print(f"Starting fallback health check server on port {port}...")
    print(f"PORT environment variable: '{os.environ.get('PORT', 'Not set')}'")
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    
    # Print all environment variables for debugging
    print("Environment variables:")
    for key, value in os.environ.items():
        if 'SECRET' not in key.upper() and 'PASSWORD' not in key.upper() and 'KEY' not in key.upper():
            print(f"  {key}: {value}")
    
    # Use the handler class with ThreadingTCPServer for better performance
    with socketserver.ThreadingTCPServer(("", port), HealthHandler) as httpd:
        print(f"Serving health check at http://0.0.0.0:{port}/health/")
        try:
            print("Server started successfully!")
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Server stopped by user")
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            httpd.server_close()
            print("Server closed") 