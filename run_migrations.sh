#!/bin/bash

# Exit on error
set -e

echo "Starting database migrations..."

# Run migrations
echo "Running migrations..."
python manage.py migrate

echo "Migrations completed successfully!" 