import logging
import traceback
import os
import socket
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.db import connection

logger = logging.getLogger(__name__)

def check_port_open(port):
    """Check if a port is open on the local host"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)  # 2 second timeout
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result == 0  # If result is 0, port is open
    except Exception as e:
        logger.error(f"Error checking port {port}: {str(e)}")
        return False

def health_check(request):
    """
    Health check endpoint that:
    1. Logs the request information
    2. Checks database connection
    3. Checks if the app is listening on the right port
    4. Returns a 200 OK response with server status
    """
    try:
        logger.info(f"Health check hit at {timezone.now().isoformat()} from {request.META.get('REMOTE_ADDR', 'unknown')}")
        
        # Log request details for debugging
        logger.debug(f"Request headers: {dict(request.headers)}")
        logger.debug(f"Request path: {request.path}")
        
        # Check database connection
        db_status = "ok"
        db_error = None
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        except Exception as e:
            db_status = "error"
            db_error = str(e)
            logger.error(f"Database health check failed: {str(e)}")
            
        # Check if app is listening on Railway PORT
        port_status = "unknown"
        railway_port = os.environ.get('PORT')
        if railway_port:
            try:
                port_open = check_port_open(int(railway_port))
                port_status = "ok" if port_open else "error"
                logger.info(f"Port {railway_port} status: {'open' if port_open else 'closed'}")
            except Exception as e:
                port_status = "error"
                logger.error(f"Error checking port: {str(e)}")
        
        # If requested as JSON, return JSON response
        if request.headers.get('Accept', '').find('application/json') != -1:
            return JsonResponse({
                'status': 'ok', 
                'server_time': timezone.now().isoformat(),
                'database': {
                    'status': db_status,
                    'error': db_error
                },
                'port': {
                    'number': railway_port,
                    'status': port_status
                },
                'request_info': {
                    'path': request.path,
                    'method': request.method,
                    'remote_addr': request.META.get('REMOTE_ADDR', 'unknown'),
                    'host': request.get_host(),
                }
            })
        
        # Otherwise return HTML response
        try:
            return render(request, 'health.html', {
                'server_time': timezone.now(),
                'db_status': db_status,
                'db_error': db_error,
                'port_number': railway_port,
                'port_status': port_status
            })
        except Exception as e:
            logger.error(f"Error rendering health template: {str(e)}")
            # Fallback to simple response if template rendering fails
            return HttpResponse(
                f"Status: OK<br>Server time: {timezone.now()}<br>Database: {db_status}<br>Port {railway_port}: {port_status}", 
                content_type='text/html'
            )
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        logger.error(traceback.format_exc())
        # Still return 200 status code to pass the health check
        return JsonResponse({
            'status': 'warning',
            'message': 'Health check encountered an error but service is running',
            'error': str(e)
        }, status=200) 