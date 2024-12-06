from django.db import models
from django.utils.translation import gettext_lazy as _

class RiskAlert(models.Model):
    """Model for storing risk alerts related to loan applications."""

    class AlertType(models.TextChoices):
        HIGH_RISK_APPLICATION = 'HIGH_RISK', _('High Risk Application')
        MULTIPLE_LOANS = 'MULTIPLE_LOANS', _('Multiple Active Loans')
        PAYMENT_PATTERN = 'PAYMENT_PATTERN', _('Suspicious Payment Pattern')
        RAPID_REQUESTS = 'RAPID_REQUESTS', _('Rapid Loan Requests')
        AMOUNT_SPIKE = 'AMOUNT_SPIKE', _('Unusual Amount Increase')

    class Severity(models.TextChoices):
        LOW = 'LOW', _('Low')
        MEDIUM = 'MEDIUM', _('Medium')
        HIGH = 'HIGH', _('High')
        CRITICAL = 'CRITICAL', _('Critical')

    loan_application = models.ForeignKey(
        'loans.LoanApplication',
        on_delete=models.CASCADE,
        related_name='risk_alerts'
    )
    alert_type = models.CharField(
        max_length=50,
        choices=AlertType.choices
    )
    severity = models.CharField(
        max_length=20,
        choices=Severity.choices
    )
    message = models.TextField()
    details = models.JSONField(
        null=True,
        blank=True,
        help_text=_('Additional details about the alert in JSON format')
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_('Whether this alert is still active')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('When this alert was resolved')
    )
    resolution_notes = models.TextField(
        blank=True,
        help_text=_('Notes about how the alert was resolved')
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['loan_application', 'alert_type']),
            models.Index(fields=['severity', 'is_active']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.get_severity_display()} alert for application {self.loan_application_id}: {self.get_alert_type_display()}"

    def resolve(self, notes=None):
        """Mark this alert as resolved."""
        from django.utils import timezone
        self.is_active = False
        self.resolved_at = timezone.now()
        if notes:
            self.resolution_notes = notes
        self.save()
