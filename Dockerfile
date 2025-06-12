FROM python:3.11-slim

WORKDIR /app

# Create health check script directly in the Dockerfile
RUN echo '#!/usr/bin/env python \n\
import http.server \n\
import socketserver \n\
import os \n\
import sys \n\
\n\
# Get port from environment - default to 8080 for Railway \n\
PORT = int(os.environ.get("PORT", 8080)) \n\
print(f"Starting health check server on port {PORT}") \n\
print("PORT environment variable:", os.environ.get("PORT", "Not set")) \n\
print(f"Python version: {sys.version}") \n\
print(f"Current directory: {os.getcwd()}") \n\
\n\
# Create a handler that responds with 200 OK to everything \n\
class HealthHandler(http.server.SimpleHTTPRequestHandler): \n\
    def do_GET(self): \n\
        self.send_response(200) \n\
        self.send_header("Content-type", "text/plain") \n\
        self.end_headers() \n\
        self.wfile.write(b"OK") \n\
        print(f"Health check: responded 200 OK to {self.path}") \n\
\n\
# Use the handler with simple server \n\
with socketserver.TCPServer(("", PORT), HealthHandler) as httpd: \n\
    print(f"Server running at http://0.0.0.0:{PORT}/") \n\
    print("Waiting for Railway health check...") \n\
    httpd.serve_forever()' > health_server.py

# Create the simplified.sh script that Railway is trying to run
RUN echo '#!/bin/bash\n\
echo "Running simplified.sh script"\n\
echo "Current directory: $(pwd)"\n\
echo "Content of directory: $(ls -la)"\n\
\n\
# Add logs to confirm port\n\
echo "PORT environment variable is: $PORT"\n\
\n\
# Run our health check server\n\
echo "Server started. Waiting for Railway health check..."\n\
python health_server.py' > simplified.sh

# Make the scripts executable
RUN chmod +x health_server.py
RUN chmod +x simplified.sh

# Create static directory with health check file
RUN mkdir -p staticfiles
RUN echo "OK" > staticfiles/index.html

# Expose the port
EXPOSE 8080

# Start the minimal health check server
CMD ["bash", "simplified.sh"] 