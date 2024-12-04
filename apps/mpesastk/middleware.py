"""MPesa STK Push middleware."""
import json
import logging
from django.http import JsonResponse
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)

class MPesaErrorMiddleware:
    """Middleware to handle MPesa-related errors."""

    def __init__(self, get_response):
        """Initialize middleware."""
        self.get_response = get_response

    def __call__(self, request):
        """Process request and response."""
        return self.get_response(request)

    def process_exception(self, request, exception):
        """Handle exceptions during request processing."""
        if request.path.startswith('/mpesa/api/'):
            # Log the error
            logger.error(
                f"MPesa API Error: {str(exception)} "
                f"Path: {request.path} "
                f"Method: {request.method}"
            )

            # Handle different types of errors
            if isinstance(exception, RequestException):
                # Network or API-related errors
                return JsonResponse({
                    'status': 'error',
                    'message': 'Failed to communicate with MPesa. Please try again.',
                    'error_type': 'network_error'
                }, status=503)
            
            elif isinstance(exception, json.JSONDecodeError):
                # Invalid JSON in request/response
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid request format',
                    'error_type': 'invalid_format'
                }, status=400)
            
            elif isinstance(exception, ValueError):
                # Validation errors
                return JsonResponse({
                    'status': 'error',
                    'message': str(exception),
                    'error_type': 'validation_error'
                }, status=400)
            
            else:
                # Other unexpected errors
                return JsonResponse({
                    'status': 'error',
                    'message': 'An unexpected error occurred',
                    'error_type': 'internal_error'
                }, status=500)
        
        return None  # Let Django handle non-MPesa errors
