"""
Minimal Flask application to serve a health check endpoint.
This is a fallback if Django's health check isn't working.
"""
import os
from flask import Flask

app = Flask(__name__)

@app.route("/health/")
def health_check():
    """Health check endpoint for Railway"""
    return {"status": "ok"}

if __name__ == "__main__":
    # Get port from environment variable or default to 8000
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port) 