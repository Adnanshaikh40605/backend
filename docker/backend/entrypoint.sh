#!/bin/bash

# Wait for database to be ready
echo "Waiting for PostgreSQL..."
wait-for-db.sh

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Create superuser if needed (customize this as required)
# python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@example.com', 'adminpassword')"

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --no-input

# Execute the passed command
exec "$@" 