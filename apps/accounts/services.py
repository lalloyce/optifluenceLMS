"""Services for account management."""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from .models import User, AuditLog
from .audit import log_event

class EmailService:
    @staticmethod
    def send_verification_email(request, user):
        """Send email verification to user."""
        subject = "Verify your email address"
        template = "accounts/emails/verify_email.html"
        context = {
            "user": user,
            "verification_url": request.build_absolute_uri(
                f"/verify-email/{user.email_verification_token}/"
            )
        }
        
        return send_mail(
            subject=subject,
            message=render_to_string(template, context),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=render_to_string(template, context),
            fail_silently=False
        )

    @staticmethod
    def send_password_reset_email(request, user):
        """Send password reset email to user."""
        subject = "Reset your password"
        template = "accounts/emails/password_reset.html"
        context = {
            "user": user,
            "reset_url": request.build_absolute_uri(
                f"/password-reset-confirm/{user.password_reset_token}/"
            )
        }
        
        return send_mail(
            subject=subject,
            message=render_to_string(template, context),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=render_to_string(template, context),
            fail_silently=False
        )

class UserService:
    @staticmethod
    def create_user(form_data):
        """Create a new user account."""
        user = form_data.save(commit=False)
        user.is_active = True
        user.save()
        
        log_event(
            None,
            AuditLog.EventType.ACCOUNT_CREATE,
            "New user account created",
            user=user,
            status='SUCCESS'
        )
        
        return user

    @staticmethod
    def verify_email(token):
        """Verify user's email address."""
        user = User.objects.get(email_verification_token=token)
        
        if (timezone.now() - user.email_verification_token_created).total_seconds() > 900:  # 15 minutes
            raise ValueError("Token expired")
            
        user.is_email_verified = True
        user.email_verification_token = None
        user.email_verification_token_created = None
        user.save()
        
        return user
