#!/bin/bash
# This is the script Railway is trying to run

# Print debug info
echo "Running simplified.sh script"
echo "Current directory: $(pwd)"
echo "Content of directory: $(ls -la)"

echo "PORT environment variable is: $PORT"

# Apply migrations
echo "Applying migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Django on the correct network interface
echo "Starting Django on 0.0.0.0:$PORT..."
python manage.py runserver 0.0.0.0:$PORT 