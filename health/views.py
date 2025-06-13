import logging
import os
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.shortcuts import render

logger = logging.getLogger(__name__)

def health_check(request):
    """
    Simple health check endpoint that returns status information
    """
    data = {
        "status": "healthy",
        "timestamp": timezone.now().isoformat(),
        "service": "Django Blog API",
        "version": "1.0.0"
    }
    return JsonResponse(data)

def railway_health(request):
    """
    Dedicated endpoint for Railway health checks.
    """
    try:
        logger.info(f"Railway health check received at {timezone.now().isoformat()}")
        return JsonResponse({"status": "ok"}, status=200)
    except Exception as e:
        logger.error(f"Railway health check error: {str(e)}")
        return HttpResponse("OK", status=200, content_type="text/plain")

def railway_health_html(request):
    """
    HTML version of the health check for Railway.
    """
    try:
        logger.info(f"Railway HTML health check received at {timezone.now().isoformat()}")
        return render(request, 'health/ok.html')
    except Exception as e:
        logger.error(f"Railway HTML health check error: {str(e)}")
        return HttpResponse("OK", status=200, content_type="text/plain")

def detailed_health(request):
    """
    More detailed health check that returns JSON with system information.
    """
    try:
        data = {
            "status": "ok",
            "timestamp": timezone.now().isoformat(),
            "environment": os.environ.get("ENVIRONMENT", "unknown"),
            "debug_mode": os.environ.get("DEBUG", "False"),
            "railway_app": True,
        }
        return JsonResponse(data, status=200)
    except Exception as e:
        logger.error(f"Detailed health check error: {str(e)}")
        return JsonResponse({"status": "ok", "error": str(e)}, status=200) 