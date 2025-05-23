"""
Simple test views to diagnose 400 Bad Request issues
"""
from django.http import HttpResponse

def simple_test(request):
    """Extremely simple view that returns plain text"""
    return HttpResponse("Hello from test_views.py", content_type="text/plain") 