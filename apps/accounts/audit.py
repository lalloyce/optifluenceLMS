"""
Utility module for handling audit logging in the accounts app.
"""
from typing import Optional, Dict, Any, Union
from django.http import HttpRequest
from .models import AuditLog, User


def log_event(
    request: HttpRequest,
    event_type: str,
    description: str,
    user: Optional[User] = None,
    status: str = 'SUCCESS',
    additional_data: Optional[Dict[str, Any]] = None
) -> AuditLog:
    """
    Create an audit log entry for a user event.
    
    Args:
        request: The HTTP request object
        event_type: Type of event from AuditLog.EventType
        description: Description of the event
        user: User object (optional)
        status: Status of the event (SUCCESS, FAILURE, WARNING)
        additional_data: Any additional data to store with the event
    
    Returns:
        AuditLog: The created audit log entry
    """
    # Get the user from request if not provided
    if user is None and request.user.is_authenticated:
        user = request.user
    
    # Get IP address from request
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip_address = x_forwarded_for.split(',')[0]
    else:
        ip_address = request.META.get('REMOTE_ADDR')
    
    # Create and return the audit log entry
    return AuditLog.objects.create(
        user=user,
        event_type=event_type,
        event_description=description,
        ip_address=ip_address,
        user_agent=request.META.get('HTTP_USER_AGENT', ''),
        status=status,
        additional_data=additional_data
    )


def get_client_ip(request: HttpRequest) -> str:
    """Get client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR', '')
