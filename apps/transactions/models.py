from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.conf import settings
from apps.loans.models import Loan


class Transaction(models.Model):
    """Model for tracking all financial transactions."""
    
    class TransactionType(models.TextChoices):
        DISBURSEMENT = 'DISBURSEMENT', _('Loan Disbursement')
        REPAYMENT = 'REPAYMENT', _('Loan Repayment')
        PENALTY = 'PENALTY', _('Late Payment Penalty')
        FEE = 'FEE', _('Processing Fee')
        OTHER = 'OTHER', _('Other')
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        COMPLETED = 'COMPLETED', _('Completed')
        FAILED = 'FAILED', _('Failed')
        REVERSED = 'REVERSED', _('Reversed')
    
    loan = models.ForeignKey(
        Loan,
        on_delete=models.PROTECT,
        related_name='transaction_records'
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TransactionType.choices
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
    transaction_date = models.DateTimeField(auto_now_add=True)
    reference_number = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='processed_transactions'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('transaction')
        verbose_name_plural = _('transactions')
        ordering = ['-transaction_date']
    
    def __str__(self):
        return f"{self.reference_number} - {self.get_transaction_type_display()}"

    def get_transaction_type_color(self):
        """Get the Bootstrap color class for the transaction type."""
        type_colors = {
            self.TransactionType.DISBURSEMENT: 'success',
            self.TransactionType.REPAYMENT: 'primary',
            self.TransactionType.PENALTY: 'danger',
            self.TransactionType.FEE: 'warning',
            self.TransactionType.OTHER: 'secondary',
        }
        return type_colors.get(self.transaction_type, 'secondary')

    def get_status_color(self):
        """Get the Bootstrap color class for the transaction status."""
        status_colors = {
            self.Status.PENDING: 'warning',
            self.Status.COMPLETED: 'success',
            self.Status.FAILED: 'danger',
            self.Status.REVERSED: 'secondary',
        }
        return status_colors.get(self.status, 'secondary')

    def get_amount_display(self):
        """Get formatted amount with sign based on transaction type."""
        if self.transaction_type in [self.TransactionType.REPAYMENT, self.TransactionType.PENALTY, self.TransactionType.FEE]:
            return f"-{self.amount:,.2f}"
        return f"+{self.amount:,.2f}"


class RepaymentSchedule(models.Model):
    """Model for tracking loan repayment schedules."""
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        PAID = 'PAID', _('Paid')
        OVERDUE = 'OVERDUE', _('Overdue')
        DEFAULTED = 'DEFAULTED', _('Defaulted')
    
    loan = models.ForeignKey(
        Loan,
        on_delete=models.CASCADE,
        related_name='repayment_schedules'
    )
    installment_number = models.IntegerField()
    due_date = models.DateTimeField()
    principal_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    interest_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    penalty_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    paid_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    paid_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('repayment schedule')
        verbose_name_plural = _('repayment schedules')
        ordering = ['due_date']
        unique_together = ['loan', 'installment_number']
    
    def __str__(self):
        return f"Loan {self.loan.application_number} - Installment {self.installment_number}"
