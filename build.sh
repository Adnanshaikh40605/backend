#!/bin/bash

# Exit on error
set -e

echo "🚀 Starting build process..."

# Install Python dependencies (in case they weren't installed in Dockerfile)
if [ "${SKIP_PIP}" != "true" ]; then
  echo "📦 Installing Python dependencies..."
  pip install -r requirements.txt
fi

# Collect static files
echo "🗂️ Collecting static files..."
python manage.py collectstatic --noinput

# Wait for PostgreSQL to be available
echo "⏳ Waiting for PostgreSQL to be available..."
python -c "
import socket
import time
import sys

host = 'postgres.railway.internal' if 'railway.internal' in socket.gethostbyname_ex('localhost')[0] else 'switchyard.proxy.rlwy.net'
port = 5432 if 'railway.internal' in socket.gethostbyname_ex('localhost')[0] else 47148

print(f'Checking PostgreSQL connection to {host}:{port}')

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
timeout = 30
start_time = time.time()

while True:
    try:
        s.connect((host, port))
        s.close()
        print('PostgreSQL is available!')
        break
    except socket.error:
        if time.time() - start_time > timeout:
            print('Timed out waiting for PostgreSQL')
            sys.exit(1)
        time.sleep(1)
        print('.', end='', flush=True)
"

# Run migrations
echo "🔄 Running database migrations..."
python manage.py migrate --noinput

echo "✅ Build completed successfully!" 