from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import resolve, reverse
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages


class SessionManagementMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            # Check if the current URL requires authentication
            current_url = resolve(request.path_info).url_name
            current_namespace = resolve(request.path_info).namespace
            current_url_name = f"{current_namespace}:{current_url}" if current_namespace else current_url

            # Get list of public URLs from settings, default to empty list if not set
            public_urls = getattr(settings, 'PUBLIC_URLS', [])

            # If URL is public or user is authenticated, proceed with session management
            if current_url_name in public_urls or hasattr(request, 'user') and request.user.is_authenticated:
                if hasattr(request, 'user') and request.user.is_authenticated:
                    # Get the current time
                    now = timezone.now()
                    
                    # Get the last activity time from the session
                    last_activity = request.session.get('last_activity')
                    
                    if last_activity:
                        # Convert the ISO formatted string back to datetime
                        last_activity = timezone.datetime.fromisoformat(last_activity)
                        
                        # Check if the session has expired
                        if now > last_activity + timedelta(seconds=settings.SESSION_COOKIE_AGE):
                            # Clear the session and logout the user
                            logout(request)
                            messages.warning(request, 'Your session has expired. Please log in again.')
                            return redirect(settings.LOGIN_URL)
                    
                    # Update the last activity time
                    request.session['last_activity'] = now.isoformat()
            
            # If URL requires authentication and user is not authenticated
            elif not current_url_name in public_urls and (not hasattr(request, 'user') or not request.user.is_authenticated):
                messages.warning(request, 'Please log in to access this page.')
                return redirect(f"{settings.LOGIN_URL}?next={request.path}")

            response = self.get_response(request)
            return response
            
        except Exception as e:
            # Log the error (you should configure proper logging)
            print(f"Session management error: {str(e)}")
            # Continue with the request even if session management fails
            return self.get_response(request)
