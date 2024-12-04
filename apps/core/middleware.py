"""Core middleware implementations."""
import time
from django.core.cache import cache
from django.http import JsonResponse
from django.conf import settings

class RateLimitMiddleware:
    """Global rate limiting middleware."""
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Default rate limits
        self.rate_limits = getattr(settings, 'RATE_LIMITS', {
            'login': {'limit': 5, 'period': 300},  # 5 attempts per 5 minutes
            'register': {'limit': 3, 'period': 3600},  # 3 attempts per hour
            'password_reset': {'limit': 3, 'period': 3600},  # 3 attempts per hour
            'verify_email': {'limit': 3, 'period': 3600},  # 3 attempts per hour
        })

    def __call__(self, request):
        # Skip rate limiting for non-targeted paths
        path = request.path.lstrip('/')
        rate_limit = next((v for k, v in self.rate_limits.items() if k in path), None)
        
        if rate_limit and request.method == 'POST':
            if self._is_rate_limited(request, path, rate_limit):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Too many attempts. Please try again later.'
                }, status=429)
        
        return self.get_response(request)
    
    def _is_rate_limited(self, request, path_key, rate_limit):
        """Check if the request should be rate limited."""
        cache_key = f"ratelimit:{path_key}:{request.META.get('REMOTE_ADDR', '')}"
        
        # Get current count and timestamp
        cache_data = cache.get(cache_key, {'count': 0, 'timestamp': time.time()})
        
        # Reset count if period has passed
        if time.time() - cache_data['timestamp'] > rate_limit['period']:
            cache_data = {'count': 0, 'timestamp': time.time()}
        
        # Increment count
        cache_data['count'] += 1
        cache.set(cache_key, cache_data, rate_limit['period'])
        
        return cache_data['count'] > rate_limit['limit']
