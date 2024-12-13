from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.conf import settings
from apps.customers.models import Customer
from apps.loans.models import Loan  # Import the Loan model directly

class Transaction(models.Model):
    """Model for tracking all financial transactions."""
    
    class TransactionType(models.TextChoices):
        MOBILE_MONEY = 'MOBILE_MONEY', _('Mobile Money')
        BANK_TRANSFER = 'BANK_TRANSFER', _('Bank Transfer')
        CASH = 'CASH', _('Cash')
        CHECK = 'CHECK', _('Check')
        OTHER = 'OTHER', _('Other')
        DISBURSEMENT = 'DISBURSEMENT', _('Loan Disbursement')
        REPAYMENT = 'REPAYMENT', _('Loan Repayment')
        PENALTY = 'PENALTY', _('Late Payment Penalty')
        FEE = 'FEE', _('Processing Fee')
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        COMPLETED = 'COMPLETED', _('Completed')
        FAILED = 'FAILED', _('Failed')
        REVERSED = 'REVERSED', _('Reversed')
    
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='transactions',
        null=True,  # Allow null initially
        blank=True
    )
    loan = models.ForeignKey(
        Loan,
        on_delete=models.PROTECT,
        related_name='transactions'
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
    transaction_date = models.DateTimeField(default=timezone.now)
    reference_number = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
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
        return f"{self.get_transaction_type_display()} - {self.amount} - {self.customer}"

    def get_transaction_type_color(self):
        """Get the Bootstrap color class for the transaction type."""
        color_map = {
            self.TransactionType.MOBILE_MONEY: 'success',
            self.TransactionType.BANK_TRANSFER: 'primary',
            self.TransactionType.CASH: 'info',
            self.TransactionType.CHECK: 'warning',
            self.TransactionType.DISBURSEMENT: 'success',
            self.TransactionType.REPAYMENT: 'primary',
            self.TransactionType.PENALTY: 'danger',
            self.TransactionType.OTHER: 'secondary',
            self.TransactionType.FEE: 'warning',
        }
        return color_map.get(self.transaction_type, 'secondary')

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
    
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE, related_name='transaction_repayment_schedules')  # Use the correct string reference

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
