#!/usr/bin/env python
"""
Standalone health check view that can be imported directly.
"""
from django.http import JsonResponse, HttpResponse

def health_check(request):
    """Ultra simple health check that returns a 200 OK"""
    try:
        return JsonResponse({"status": "ok"})
    except Exception as e:
        # Fallback to plain text if JSON fails
        return HttpResponse("OK", content_type="text/plain") 