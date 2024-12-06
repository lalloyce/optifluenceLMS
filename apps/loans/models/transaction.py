from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.conf import settings
from apps.accounts.models import User
from .loan import Loan
from .repayment import RepaymentSchedule


class Transaction(models.Model):
    """Model for loan transactions."""
    
    class Type(models.TextChoices):
        DISBURSEMENT = 'DISBURSEMENT', _('Disbursement')
        REPAYMENT = 'REPAYMENT', _('Repayment')
        PENALTY = 'PENALTY', _('Penalty')
        WAIVER = 'WAIVER', _('Waiver')
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        COMPLETED = 'COMPLETED', _('Completed')
        FAILED = 'FAILED', _('Failed')
        REVERSED = 'REVERSED', _('Reversed')
    
    loan = models.ForeignKey(
        Loan,
        on_delete=models.CASCADE,
        related_name='loan_transactions'
    )
    repayment_schedule = models.ForeignKey(
        RepaymentSchedule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='schedule_transactions'
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=Type.choices
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    reference_number = models.CharField(
        max_length=50,
        unique=True
    )
    payment_method = models.CharField(
        max_length=50,
        null=True,
        blank=True
    )
    payment_details = models.JSONField(
        null=True,
        blank=True,
        help_text=_('Additional payment details in JSON format')
    )
    notes = models.TextField(null=True, blank=True)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='loan_processed_transactions'
    )
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['reference_number']),
            models.Index(fields=['loan', 'transaction_type', 'status']),
        ]
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.reference_number}"
    
    def save(self, *args, **kwargs):
        if not self.reference_number:
            prefix = {
                self.Type.DISBURSEMENT: 'DSB',
                self.Type.REPAYMENT: 'RPY',
                self.Type.PENALTY: 'PEN',
                self.Type.WAIVER: 'WVR'
            }.get(self.transaction_type, 'TXN')
            
            timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
            self.reference_number = f"{prefix}{timestamp}"
        
        super().save(*args, **kwargs)
    
    def complete_transaction(self, user):
        """Mark transaction as completed and update related records."""
        if self.status != self.Status.PENDING:
            raise ValueError("Only pending transactions can be completed.")
        
        self.status = self.Status.COMPLETED
        self.processed_by = user
        self.processed_at = timezone.now()
        
        if self.transaction_type == self.Type.REPAYMENT and self.repayment_schedule:
            self.repayment_schedule.paid_amount += self.amount
            self.repayment_schedule.paid_date = timezone.now().date()
            self.repayment_schedule.update_status()
            self.repayment_schedule.save()
        
        self.save()
    
    def reverse_transaction(self, user, notes=None):
        """Reverse a completed transaction."""
        if self.status != self.Status.COMPLETED:
            raise ValueError("Only completed transactions can be reversed.")
        
        if self.transaction_type == self.Type.REPAYMENT and self.repayment_schedule:
            self.repayment_schedule.paid_amount -= self.amount
            self.repayment_schedule.update_status()
            if self.repayment_schedule.paid_amount == 0:
                self.repayment_schedule.paid_date = None
            self.repayment_schedule.save()
        
        self.status = self.Status.REVERSED
        self.processed_by = user
        self.processed_at = timezone.now()
        if notes:
            self.notes = (self.notes or '') + f"\nReversed: {notes}"
        self.save()
