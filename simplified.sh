#!/bin/bash
set -x

# Set default port
PORT=${PORT:-8000}
echo "Using PORT: $PORT"

# Create health check file
mkdir -p staticfiles
echo "OK" > staticfiles/health.html

# Run migrations
python manage.py migrate --noinput || true

# Collect static files
python manage.py collectstatic --noinput || true

# Start with our combined application
gunicorn --bind 0.0.0.0:$PORT --workers 2 wsgi_health:application 