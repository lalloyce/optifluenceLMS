from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Q, F, Max
from ..models import Loan, LoanApplication, RiskAlert
from ..models.repayment import RepaymentSchedule
from decimal import Decimal

class RiskAlertService:
    """Service for managing risk alerts."""
    
    def __init__(self, loan_application):
        self.application = loan_application
        self.customer = loan_application.customer
        
    def check_all_risk_patterns(self):
        """Check for all risk patterns and create alerts as needed."""
        self.check_high_risk_application()
        self.check_multiple_active_loans()
        self.check_payment_patterns()
        self.check_rapid_requests()
        self.check_amount_spike()
        
    def create_alert(self, alert_type, severity, message, details=None):
        """Create a new risk alert."""
        alert = RiskAlert.objects.create(
            loan_application=self.application,
            alert_type=alert_type,
            severity=severity,
            message=message,
            details=details
        )
        
        # Send notification for critical alerts
        from .alert_notifications import AlertNotificationService
        AlertNotificationService.notify_critical_alert(alert)
        
        return alert
        
    def check_high_risk_application(self):
        """Check if loan application has high risk score."""
        if self.application.risk_score and self.application.risk_score < 40:
            self.create_alert(
                RiskAlert.AlertType.HIGH_RISK_APPLICATION,
                RiskAlert.Severity.HIGH,
                f"High risk loan application with score {self.application.risk_score}",
                {
                    'risk_score': self.application.risk_score,
                    'risk_factors': self.application.risk_factors
                }
            )
            
    def check_multiple_active_loans(self):
        """Check if customer has multiple active loans."""
        active_loans = Loan.objects.filter(
            application__customer=self.customer,
            status=Loan.Status.ACTIVE
        )
        
        active_count = active_loans.count()
        if active_count >= 2:
            severity = RiskAlert.Severity.CRITICAL if active_count > 2 else RiskAlert.Severity.HIGH
            
            self.create_alert(
                RiskAlert.AlertType.MULTIPLE_LOANS,
                severity,
                f"Customer has {active_count} active loans",
                {
                    'active_loan_count': active_count,
                    'active_loan_ids': list(active_loans.values_list('id', flat=True))
                }
            )
            
    def check_payment_patterns(self):
        """Check for suspicious payment patterns."""
        # Check for consistently late payments
        past_schedules = RepaymentSchedule.objects.filter(
            loan__application__customer=self.customer,
            status=RepaymentSchedule.Status.PAID
        ).order_by('due_date')
        
        late_count = past_schedules.filter(
            paid_date__gt=F('due_date')
        ).count()
        
        total_count = past_schedules.count()
        
        if total_count >= 5 and (late_count / total_count) > 0.6:
            self.create_alert(
                RiskAlert.AlertType.PAYMENT_PATTERN,
                RiskAlert.Severity.MEDIUM,
                f"Customer has high rate of late payments ({late_count}/{total_count})",
                {
                    'late_payment_ratio': late_count / total_count,
                    'late_count': late_count,
                    'total_count': total_count
                }
            )
            
    def check_rapid_requests(self):
        """Check for unusually rapid loan requests."""
        recent_applications = LoanApplication.objects.filter(
            customer=self.customer,
            created_at__gte=timezone.now() - timedelta(days=30)
        ).exclude(pk=self.application.pk)
        
        if recent_applications.count() >= 2:
            self.create_alert(
                RiskAlert.AlertType.RAPID_REQUESTS,
                RiskAlert.Severity.MEDIUM,
                f"Multiple loan applications in the past 30 days",
                {
                    'recent_application_count': recent_applications.count(),
                    'application_dates': list(recent_applications.values_list('created_at', flat=True))
                }
            )
            
    def check_amount_spike(self):
        """Check for unusual increases in requested loan amounts."""
        previous_max = Loan.objects.filter(
            application__customer=self.customer,
            status__in=[Loan.Status.CLOSED, Loan.Status.ACTIVE]
        ).aggregate(max_amount=Max('amount_approved'))['max_amount']
        
        if previous_max and self.application.amount_requested > previous_max * Decimal('2.0'):
            self.create_alert(
                RiskAlert.AlertType.AMOUNT_SPIKE,
                RiskAlert.Severity.HIGH,
                f"Requested amount is more than double the previous maximum",
                {
                    'previous_max': float(previous_max),
                    'requested_amount': float(self.application.amount_requested),
                    'increase_ratio': float(self.application.amount_requested / previous_max)
                }
            )
            
    @classmethod
    def get_active_alerts_summary(cls):
        """Get summary of all active alerts."""
        return {
            'total_active': RiskAlert.objects.filter(is_active=True).count(),
            'by_severity': dict(
                RiskAlert.objects.filter(is_active=True)
                .values('severity')
                .annotate(count=Count('id'))
                .values_list('severity', 'count')
            ),
            'by_type': dict(
                RiskAlert.objects.filter(is_active=True)
                .values('alert_type')
                .annotate(count=Count('id'))
                .values_list('alert_type', 'count')
            )
        }
