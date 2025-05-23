"""
Run the simple WSGI application
"""
from wsgiref.simple_server import make_server
from backend.simple_app import simple_app

if __name__ == "__main__":
    print("Starting simple WSGI server on http://localhost:8001")
    httpd = make_server('', 8001, simple_app)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server")
        httpd.server_close() 