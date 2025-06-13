FROM python:3.11-slim

WORKDIR /app

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

# Start the health check server which will then start Django
CMD ["python", "simple_health.py"] 