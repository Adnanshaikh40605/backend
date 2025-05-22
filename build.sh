#!/bin/bash

# Exit on error
set -e

echo "🚀 Starting build process..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Collect static files
echo "🗂️ Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations
echo "🔄 Running database migrations..."
python manage.py migrate

echo "✅ Build completed successfully!" 