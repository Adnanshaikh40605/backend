FROM python:3.11-slim

WORKDIR /app

# Create health check script directly in the Dockerfile
RUN echo '#!/usr/bin/env python \n\
import http.server \n\
import socketserver \n\
import os \n\
\n\
# Get port from environment \n\
PORT = int(os.environ.get("PORT", 8000)) \n\
print(f"Starting health check server on port {PORT}") \n\
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
    httpd.serve_forever()' > health_server.py

# Make the script executable
RUN chmod +x health_server.py

# Create static directory with health check file
RUN mkdir -p staticfiles
RUN echo "OK" > staticfiles/index.html

# Expose the port
EXPOSE 8080

# Start the minimal health check server
CMD ["python", "health_server.py"] 