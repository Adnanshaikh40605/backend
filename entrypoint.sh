#!/bin/bash

# Exit on error
set -e

echo "🚀 Starting application..."

# Run migrations
echo "🔄 Running database migrations..."
python manage.py migrate

# Start Gunicorn
echo "🌐 Starting Gunicorn server..."
gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT 