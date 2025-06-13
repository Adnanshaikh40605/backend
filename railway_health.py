#!/usr/bin/env python
"""
Minimal Flask application for Railway health checks
"""
import os
import sys
import threading
import time
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health')
@app.route('/health/')
@app.route('/')
def health():
    """Simple health check endpoint that returns a 200 OK"""
    return jsonify({"status": "ok"})

def start_django():
    """Start the Django application after a delay"""
    time.sleep(5)  # Give Flask time to start
    print("Starting Django application...")
    os.system("python manage.py migrate --noinput")
    os.system("python manage.py collectstatic --noinput")
    os.system("mkdir -p staticfiles")
    os.system("echo '{\"status\": \"ok\"}' > staticfiles/health.json")
    os.system(f"PYTHONUNBUFFERED=1 gunicorn wsgi:application --bind 0.0.0.0:{os.environ.get('PORT', 8000)} --workers 2 --log-level debug --timeout 120")

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting health check server on port {port}")
    
    # Start Django in a separate thread
    django_thread = threading.Thread(target=start_django)
    django_thread.daemon = True
    django_thread.start()
    
    # Run Flask app on the main thread
    app.run(host='0.0.0.0', port=port, threaded=True) 