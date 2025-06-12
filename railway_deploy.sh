#!/bin/bash
# This script is specifically for Railway deployment
# It only uses the built-in Python HTTP server with no dependencies

# Echo all commands
set -x

# Get PORT from environment or use default
PORT=${PORT:-8000}
echo "Railway deployment script running on port $PORT"

# Create static files directory
mkdir -p staticfiles
echo "OK" > staticfiles/index.html
echo "OK" > staticfiles/railway.html

# Create a simple one-file health check server
cat > railway_health.py << 'EOF'
import http.server
import socketserver
import os

# Get port from environment
PORT = int(os.environ.get('PORT', 8000))
print(f"Starting health check server on port {PORT}")

# Create a handler that responds with 200 OK to everything
class HealthHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'OK')
        print(f"Health check: responded 200 OK to {self.path}")

# Use the handler with simple server
with socketserver.TCPServer(("", PORT), HealthHandler) as httpd:
    print(f"Server running at http://0.0.0.0:{PORT}/")
    httpd.serve_forever()
EOF

# Make health check script executable
chmod +x railway_health.py

# Run the health check server
python railway_health.py 