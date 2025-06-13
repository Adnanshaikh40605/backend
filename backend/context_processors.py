from django.conf import settings

def backend_url(request):
    """
    Add the BACKEND_URL to the template context.
    This allows templates to reference the backend URL for API calls.
    """
    return {
        'BACKEND_URL': settings.BACKEND_URL
    } 