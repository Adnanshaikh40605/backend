FROM python:3.11-slim

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Make sure startup script is executable
RUN chmod +x startup.sh
RUN chmod +x health_check.py
RUN chmod +x standalone_health.py
RUN chmod +x simple_server.py
RUN chmod +x simplified.sh
RUN chmod +x ultra_simple.sh

# Collect static files
RUN python manage.py collectstatic --noinput

# Run migrations at build time (can be skipped if you prefer to run migrations at runtime)
# RUN python manage.py migrate

# Expose port (will be overridden by Railway PORT env var)
EXPOSE 8000

# Start the application using the startup script
CMD ["bash", "startup.sh"] 