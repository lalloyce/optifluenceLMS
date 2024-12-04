from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from apps.loans.models import Loan
from apps.accounts.models import User


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
    transaction_date = models.DateTimeField(auto_now_add=True)
    reference_number = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)
    processed_by = models.ForeignKey(
        User,
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
        related_name='repayment_schedule'
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
