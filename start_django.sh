#!/bin/bash
set -e

echo "=== Starting Django Application ==="
echo "Current directory: $(pwd)"
echo "Environment variables:"
echo "PORT=$PORT"
echo "DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE"
echo "ALLOWED_HOSTS=$ALLOWED_HOSTS"
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

# Create a simple health check file that Railway can access
mkdir -p /app/staticfiles
echo '{"status":"ok"}' > /app/staticfiles/health.json

echo "Starting Gunicorn on 0.0.0.0:$PORT..."
echo "Using WSGI module: backend.wsgi:application"
exec gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --log-level debug --timeout 120 