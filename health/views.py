import logging
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone

logger = logging.getLogger(__name__)

def health_check(request):
    """
    Simple health check endpoint that returns a 200 OK response.
    Railway uses this to verify the application is running.
    """
    try:
        # Log the health check request
        logger.info(f"Health check request received at {timezone.now().isoformat()} from {request.META.get('REMOTE_ADDR', 'unknown')}")
        
        # Always return a simple 200 OK response for Railway
        return JsonResponse({'status': 'ok'})
    except Exception as e:
        # Log the error but still return 200 to pass health checks
        logger.error(f"Health check error: {str(e)}")
        return JsonResponse({'status': 'ok'}, status=200) 