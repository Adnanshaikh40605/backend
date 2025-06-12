#!/usr/bin/env python
"""
Extremely simple HTTP server that responds with 200 OK to all requests.
This is a last resort for Railway health checks if all else fails.
"""
import http.server
import os
import sys

PORT = int(os.environ.get('PORT', 8000))

class SimpleHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle all GET requests with a 200 OK response."""
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'OK')
        print(f"Responded 200 OK to {self.path}")
    
    def log_message(self, format, *args):
        """Override to simplify logging."""
        print(f"{self.address_string()} - {format % args}")

if __name__ == "__main__":
    print(f"Starting simple health check server on port {PORT}")
    server = http.server.HTTPServer(('0.0.0.0', PORT), SimpleHandler)
    
    try:
        print(f"Server running at http://0.0.0.0:{PORT}/")
        server.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped by user")
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        server.server_close()
        print("Server closed") 