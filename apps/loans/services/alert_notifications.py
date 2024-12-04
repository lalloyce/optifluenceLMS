from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth import get_user_model
from ..models import RiskAlert

User = get_user_model()

class AlertNotificationService:
    """Service for sending risk alert notifications."""
    
    @classmethod
    def notify_critical_alert(cls, alert):
        """Send notification for critical risk alerts."""
        if alert.severity != RiskAlert.Severity.CRITICAL:
            return
            
        # Get loan officers and risk managers
        recipients = User.objects.filter(
            groups__name__in=['Loan Officers', 'Risk Managers']
        ).values_list('email', flat=True)
        
        if not recipients:
            return
            
        context = {
            'alert': alert,
            'loan': alert.loan,
            'customer': alert.loan.customer,
            'alert_type': alert.get_alert_type_display(),
            'details': alert.details or {},
            'dashboard_url': f"{settings.BASE_URL}/loans/risk-dashboard/"
        }
        
        subject = f"CRITICAL RISK ALERT: {alert.get_alert_type_display()}"
        
        # Render email templates
        html_message = render_to_string(
            'loans/email/critical_alert.html',
            context
        )
        text_message = render_to_string(
            'loans/email/critical_alert.txt',
            context
        )
        
        send_mail(
            subject=subject,
            message=text_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=list(recipients),
            fail_silently=True
        )
    
    @classmethod
    def notify_high_risk_application(cls, loan):
        """Send notification for high-risk loan applications."""
        if loan.risk_score >= 40:  # Only notify for high-risk loans
            return
            
        recipients = User.objects.filter(
            groups__name='Loan Officers'
        ).values_list('email', flat=True)
        
        if not recipients:
            return
            
        context = {
            'loan': loan,
            'customer': loan.customer,
            'risk_score': loan.risk_score,
            'risk_factors': loan.risk_factors,
            'dashboard_url': f"{settings.BASE_URL}/loans/risk-dashboard/"
        }
        
        subject = f"High Risk Loan Application: {loan.reference_number}"
        
        html_message = render_to_string(
            'loans/email/high_risk_application.html',
            context
        )
        text_message = render_to_string(
            'loans/email/high_risk_application.txt',
            context
        )
        
        send_mail(
            subject=subject,
            message=text_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=list(recipients),
            fail_silently=True
        )
    
    @classmethod
    def send_daily_summary(cls):
        """Send daily summary of risk alerts."""
        from .risk_alerts import RiskAlertService
        
        recipients = User.objects.filter(
            groups__name__in=['Risk Managers']
        ).values_list('email', flat=True)
        
        if not recipients:
            return
            
        summary = RiskAlertService.get_active_alerts_summary()
        
        context = {
            'summary': summary,
            'dashboard_url': f"{settings.BASE_URL}/loans/risk-dashboard/"
        }
        
        subject = "Daily Risk Alerts Summary"
        
        html_message = render_to_string(
            'loans/email/daily_summary.html',
            context
        )
        text_message = render_to_string(
            'loans/email/daily_summary.txt',
            context
        )
        
        send_mail(
            subject=subject,
            message=text_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=list(recipients),
            fail_silently=True
        )
