FROM python:3.11-slim

WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=backend.settings

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project files
COPY . .

# Create static directory with health check file
RUN mkdir -p staticfiles
RUN echo '{"status": "ok"}' > staticfiles/health.json

# Create health directories for the minimal server
RUN mkdir -p /tmp/health
RUN echo '{"status":"ok"}' > /tmp/health/health.json

# Make all scripts executable
RUN chmod +x *.py *.sh

# Expose the port
EXPOSE 8080

# Start the minimal health server that will also start Django
CMD ["python", "minimal_health.py"] 