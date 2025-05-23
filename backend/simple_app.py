"""
Standalone WSGI application for testing
"""

def simple_app(environ, start_response):
    """
    A simple WSGI application that returns a 'Hello World' response.
    This bypasses all Django middleware and configuration.
    """
    status = '200 OK'
    headers = [('Content-type', 'text/plain')]
    start_response(status, headers)
    return [b'Hello World from simple_app.py']

# To run this standalone:
# from wsgiref.simple_server import make_server
# httpd = make_server('', 8000, simple_app)
# httpd.serve_forever() 