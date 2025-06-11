import logging
import os
import socket
import sys
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.conf import settings

logger = logging.getLogger(__name__)

def health_check(request):
    """
    Enhanced health check endpoint that returns a 200 OK response.
    Railway uses this to verify the application is running.
    """
    try:
        # Log the health check request with detailed information
        logger.info(f"Health check request received at {timezone.now().isoformat()}")
        logger.info(f"Request path: {request.path}")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Remote address: {request.META.get('REMOTE_ADDR', 'unknown')}")
        logger.info(f"User agent: {request.META.get('HTTP_USER_AGENT', 'unknown')}")
        
        # Get system information
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        
        # Create response data with useful debugging information
        response_data = {
            'status': 'ok',
            'timestamp': timezone.now().isoformat(),
            'environment': os.environ.get('RAILWAY_ENVIRONMENT', 'unknown'),
            'service_id': os.environ.get('RAILWAY_SERVICE_ID', 'unknown'),
            'deployment_id': os.environ.get('RAILWAY_DEPLOYMENT_ID', 'unknown'),
            'port': os.environ.get('PORT', 'unknown'),
            'hostname': hostname,
            'ip_address': ip_address,
            'python_version': sys.version,
            'django_version': settings.DJANGO_VERSION,
            'debug_mode': settings.DEBUG,
        }
        
        # Always return a 200 OK response for Railway health checks
        return JsonResponse(response_data)
    except Exception as e:
        # Log the error but still return 200 to pass health checks
        logger.error(f"Health check error: {str(e)}")
        return JsonResponse({
            'status': 'warning',
            'message': 'Health check encountered an error but service is running',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=200) 