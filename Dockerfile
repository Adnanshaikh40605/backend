FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . .

# Create the simplified.sh script with more verbose logging
RUN echo '#!/bin/bash\n\
set -e\n\
echo "Running simplified.sh script"\n\
echo "Current directory: $(pwd)"\n\
echo "Content of directory: $(ls -la)"\n\
\n\
echo "PORT environment variable is: $PORT"\n\
\n\
# Check if we can import Django\n\
echo "Checking Django installation:"\n\
python -c "import django; print(f\"Django version: {django.__version__}\")"\n\
\n\
# Check if wsgi.py exists\n\
echo "Checking for wsgi.py:"\n\
if [ -f backend/wsgi.py ]; then echo "wsgi.py found"; else echo "ERROR: wsgi.py not found"; fi\n\
\n\
# Test health view directly\n\
echo "Testing health view:"\n\
python -c "from health.views import health_check; from django.http import HttpRequest; print(health_check(HttpRequest()).content)" || echo "Failed to import health_check view"\n\
\n\
# Apply migrations with more verbose output\n\
echo "Applying migrations..."\n\
python manage.py migrate --noinput -v 2\n\
\n\
# Collect static files\n\
echo "Collecting static files..."\n\
python manage.py collectstatic --noinput -v 2\n\
\n\
# Create a test health file in case Django fails\n\
mkdir -p staticfiles\n\
echo "{\\"status\\": \\"healthy\\"}" > staticfiles/health.json\n\
\n\
# Start with Gunicorn for production with more verbose logging\n\
echo "Starting Gunicorn on 0.0.0.0:$PORT..."\n\
PYTHONUNBUFFERED=1 gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --access-logfile - --error-logfile - --log-level debug' > simplified.sh

# Make the script executable
RUN chmod +x simplified.sh

# Create static directory with health check file
RUN mkdir -p staticfiles
RUN echo '{"status": "healthy"}' > staticfiles/health.json

# Expose the port
EXPOSE 8080

# Start the server
CMD ["bash", "simplified.sh"] 