from django.shortcuts import render
from django.http import JsonResponse

def custom_404(request, exception):
    """
    Custom 404 handler that returns either HTML or JSON based on the request's Accept header
    """
    if request.headers.get('Accept', '').startswith('application/json'):
        # Return JSON response for API requests
        return JsonResponse({
            'error': 'Not found',
            'status_code': 404,
            'message': 'The requested resource was not found on this server.'
        }, status=404)
    else:
        # Return HTML response for browser requests
        return render(request, '404.html', {
            'title': 'Page Not Found',
            'message': 'The page you requested could not be found.'
        }, status=404) 