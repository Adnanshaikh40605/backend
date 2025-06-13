#!/bin/bash

# Exit on error
set -e

echo "Starting deployment process..."

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Run migrations
echo "Running migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start the application
echo "Starting the application..."
gunicorn backend.wsgi:application --bind 0.0.0.0:${PORT:-8000}

echo "Deployment complete!" 