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

# Make the scripts executable
RUN chmod +x *.py *.sh

# Expose the port
EXPOSE 8080

# Make the startup script executable
RUN chmod +x start_django.sh

# Start Django with our custom startup script
CMD ["./start_django.sh"] 