FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . .

# Create a simplified script for starting Django
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "=== Starting Django ==="\n\
echo "Current directory: $(pwd)"\n\
echo "Content of directory: $(ls -la)"\n\
\n\
echo "PORT environment variable is: $PORT"\n\
\n\
# Apply migrations\n\
echo "Running migrations..."\n\
python manage.py migrate --noinput\n\
\n\
# Collect static files\n\
echo "Collecting static files..."\n\
python manage.py collectstatic --noinput\n\
\n\
# Create health check file as backup\n\
mkdir -p staticfiles\n\
echo "{\\"status\\": \\"ok\\"}" > staticfiles/health.json\n\
\n\
# Start Gunicorn with standard workers (not uvicorn workers)\n\
echo "Starting Gunicorn on 0.0.0.0:$PORT..."\n\
PYTHONUNBUFFERED=1 gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --log-level debug' > simplified.sh

# Make the script executable
RUN chmod +x simplified.sh

# Create static directory with health check file
RUN mkdir -p staticfiles
RUN echo '{"status": "ok"}' > staticfiles/health.json

# Expose the port
EXPOSE 8080

# Start the server
CMD ["bash", "simplified.sh"] 