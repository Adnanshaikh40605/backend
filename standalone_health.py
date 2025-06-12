#!/usr/bin/env python
"""
Standalone HTTP server that responds to health checks.
This runs independently of the Django application.
"""
import os
import http.server
import socketserver
import threading
import time
import sys
import json
from http import HTTPStatus

class HealthRequestHandler(http.server.BaseHTTPRequestHandler):
    """Handler for health check requests."""
    
    def do_GET(self):
        """Handle GET requests."""
        print(f"[Health Server] Received request for path: {self.path}")
        
        # Always respond with 200 OK to any path
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-Type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'OK')
        print(f"[Health Server] Responded 200 OK to {self.path}")
    
    def log_message(self, format, *args):
        """Override to customize logging."""
        sys.stderr.write(f"[Health Server] {self.address_string()} - {format % args}\n")

def start_health_server(port=8081):
    """Start a health check server on the specified port."""
    try:
        # Create server
        server = socketserver.ThreadingTCPServer(("", port), HealthRequestHandler)
        print(f"[Health Server] Starting health check server on port {port}...")
        
        # Start server in a daemon thread
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True  # Don't keep the process alive
        server_thread.start()
        print(f"[Health Server] Server running at http://0.0.0.0:{port}/")
        
        return server
    except Exception as e:
        print(f"[Health Server] Error starting health server: {e}")
        return None

if __name__ == "__main__":
    # Get port from environment variable or use default
    health_port = int(os.environ.get('HEALTH_PORT', 8081))
    
    print(f"[Health Server] Starting standalone health check server on port {health_port}")
    print(f"[Health Server] Python version: {sys.version}")
    print(f"[Health Server] Current directory: {os.getcwd()}")
    
    server = start_health_server(health_port)
    
    if server:
        try:
            # Keep the main thread alive
            while True:
                time.sleep(60)
                print("[Health Server] Still alive...")
        except KeyboardInterrupt:
            print("[Health Server] Shutting down...")
            server.shutdown()
    else:
        print("[Health Server] Failed to start server") 