#!/bin/bash
set -x

# This script is the absolute simplest deployment for Railway
# It only starts a simple HTTP server that responds 200 OK to all requests

# Set default port
PORT=${PORT:-8000}
echo "Using PORT: $PORT"

# Create a static directory with health check files
mkdir -p staticfiles
echo "OK" > staticfiles/index.html
echo "OK" > staticfiles/health.html

# Start the simple server
python simple_server.py 