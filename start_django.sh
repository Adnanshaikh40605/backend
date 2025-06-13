#!/bin/bash
set -e

echo "=== Starting Django Application ==="
echo "Current directory: $(pwd)"
echo "Contents: $(ls -la)"

# Make sure static directory exists
mkdir -p staticfiles

# Copy favicon to staticfiles
if [ -f "static/favicon.ico" ]; then
  echo "Copying favicon.ico to staticfiles"
  cp static/favicon.ico staticfiles/
fi

# Create health check file
echo '{"status": "ok"}' > staticfiles/health.json

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn on 0.0.0.0:$PORT..."
exec gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --log-level debug --timeout 120 