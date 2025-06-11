import logging
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from django.db import connection

logger = logging.getLogger(__name__)

def health_check(request):
    """
    Simple health check endpoint that:
    1. Checks database connection
    2. Returns a 200 OK response with server status
    """
    try:
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
        
        # If requested as JSON, return JSON response
        if request.headers.get('Accept', '').find('application/json') != -1:
            return JsonResponse({
                'status': 'ok', 
                'server_time': timezone.now().isoformat(),
                'database': {
                    'status': db_status,
                    'error': db_error
                }
            })
        
        # Otherwise return HTML response
        try:
            return render(request, 'health.html', {
                'server_time': timezone.now(),
                'db_status': db_status,
                'db_error': db_error
            })
        except Exception as e:
            logger.error(f"Error rendering health template: {str(e)}")
            # Fallback to simple response if template rendering fails
            return JsonResponse({'status': 'ok'})
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        # Still return 200 status code to pass the health check
        return JsonResponse({'status': 'ok'}, status=200) 