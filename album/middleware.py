"""
Custom middleware for error handling and logging.
"""
import logging
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from .logging_utils import log_error, log_info

logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(MiddlewareMixin):
    """
    Middleware to handle exceptions and log them appropriately.
    """
    
    def process_exception(self, request, exception):
        """
        Process exceptions and log them with context.
        """
        log_error(exception, user=request.user, request=request)
        
        # Return appropriate response based on request type
        if request.path.startswith('/api/'):
            return JsonResponse({
                'error': 'Internal server error',
                'message': 'An unexpected error occurred'
            }, status=500)
        
        # For regular requests, let Django handle the error normally
        return None


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add security headers to responses.
    """
    
    def process_response(self, request, response):
        """
        Add security headers to the response.
        """
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Add CSP header if not already present
        if 'Content-Security-Policy' not in response:
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; "
                "font-src 'self' https://fonts.gstatic.com; "
                "img-src 'self' data: https://cdn.jsdelivr.net; "
                "connect-src 'self' https://cdn.jsdelivr.net;"
            )
        
        return response


        # Log the performance
        log_info(f"{request.method} {request.path} - {duration:.2f}s - User: {user_display} (ID: {user_id}) - IP: {ip_address}")

class AlbumAdminMiddleware(MiddlewareMixin):
    def process_request(self, request):
        logger.info(f"User: {request.user}, Authenticated: {request.user.is_authenticated}")
        if request.user.is_authenticated:
            # Set user roles
            request.user.is_site_admin = request.user.is_superuser
            # Album admin is now determined per-album basis (album ownership)
            # No longer a global group - users are admins of albums they own
            request.user.is_album_owner = hasattr(request.user, 'owned_albums') and request.user.owned_albums.exists()
            # Viewer is default for authenticated users
            request.user.is_viewer = not request.user.is_site_admin
            logger.info(f"User {request.user}: site_admin={request.user.is_site_admin}, album_owner={request.user.is_album_owner}, viewer={request.user.is_viewer}")
        else:
            request.user.is_album_owner = False


class PerformanceLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log slow requests.
    """
    
    def process_request(self, request):
        """
        Start timing the request.
        """
        import time
        request._start_time = time.time()
    
    def process_response(self, request, response):
        """
        Log slow requests.
        """
        if hasattr(request, '_start_time'):
            import time
            duration = time.time() - request._start_time
            
            # Log all requests
            log_info(
                f"{request.method} {request.path} - {response.status_code} ({duration:.2f}s)",
                user=request.user,
                request=request
            )
            
            # Log slow requests
            if duration > 2.0:  # Log requests taking more than 2 seconds
                logger.warning(
                    f"Slow request: {request.method} {request.path} took {duration:.2f}s"
                )
        
        return response
