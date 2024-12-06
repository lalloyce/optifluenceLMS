from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.customers.models import Customer
from apps.accounts.models import User
from django.utils import timezone
from datetime import timedelta
import uuid
import numpy_financial as npf


class LoanProduct(models.Model):
    """Model for different types of loan products."""
    
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    minimum_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    maximum_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    minimum_term = models.IntegerField()
    maximum_term = models.IntegerField()
    processing_fee = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Risk-based limits
    high_risk_max_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0,
        help_text=_('Maximum amount for high-risk loans (score < 40)')
    )
    medium_risk_max_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0,
        help_text=_('Maximum amount for medium-risk loans (score 40-59)')
    )
    moderate_risk_max_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0,
        help_text=_('Maximum amount for moderate-risk loans (score 60-79)')
    )
    
    # Risk thresholds for automatic approval/rejection
    auto_reject_below = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=30,
        help_text=_('Automatically reject loans with risk score below this value')
    )
    auto_approve_above = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=80,
        help_text=_('Automatically approve loans with risk score above this value')
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('loan product')
        verbose_name_plural = _('loan products')
    
    def __str__(self):
        return self.name
    
    def get_max_amount_for_risk_score(self, risk_score):
        """Get maximum allowed amount based on risk score."""
        if risk_score >= 80:
            return self.maximum_amount
        elif risk_score >= 60:
            return self.moderate_risk_max_amount
        elif risk_score >= 40:
            return self.medium_risk_max_amount
        else:
            return self.high_risk_max_amount


class Loan(models.Model):
    """Model for individual loans."""
    
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', _('Draft')
        PENDING = 'PENDING', _('Pending Approval')
        APPROVED = 'APPROVED', _('Approved')
        REJECTED = 'REJECTED', _('Rejected')
        DISBURSED = 'DISBURSED', _('Disbursed')
        CLOSED = 'CLOSED', _('Closed')
        DEFAULTED = 'DEFAULTED', _('Defaulted')
    
    class RiskLevel(models.TextChoices):
        LOW = 'LOW', _('Low Risk')
        MODERATE = 'MODERATE', _('Moderate Risk')
        MEDIUM = 'MEDIUM', _('Medium Risk')
        HIGH = 'HIGH', _('High Risk')
    
    loan_product = models.ForeignKey(
        LoanProduct,
        on_delete=models.PROTECT,
        related_name='loans'
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='loans'
    )
    loan_officer = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='handled_loans'
    )
    
    # Loan Details
    application_number = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    term_months = models.IntegerField(validators=[MinValueValidator(1)])
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    processing_fee = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Risk Assessment
    risk_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Calculated risk score (0-100)')
    )
    risk_level = models.CharField(
        max_length=20,
        choices=RiskLevel.choices,
        null=True,
        blank=True
    )
    risk_factors = models.JSONField(
        null=True,
        blank=True,
        help_text=_('Detailed risk assessment factors')
    )
    risk_notes = models.TextField(
        null=True,
        blank=True,
        help_text=_('Additional notes about risk assessment')
    )
    
    # Dates
    application_date = models.DateTimeField(auto_now_add=True)
    approval_date = models.DateTimeField(null=True, blank=True)
    disbursement_date = models.DateTimeField(null=True, blank=True)
    maturity_date = models.DateTimeField(null=True, blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )
    
    # Additional Information
    purpose = models.TextField()
    notes = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('loan')
        verbose_name_plural = _('loans')
        ordering = ['-application_date']
    
    def __str__(self):
        return f"Loan {self.application_number} - {self.customer.get_full_name()}"
        
    def get_status_display(self):
        """Get the display name of the current status."""
        return self.get_status_display()

    def get_status_color(self):
        """Get the Bootstrap color class for the current status."""
        status_colors = {
            self.Status.DRAFT: 'secondary',
            self.Status.PENDING: 'warning',
            self.Status.APPROVED: 'info',
            self.Status.REJECTED: 'danger',
            self.Status.DISBURSED: 'success',
            self.Status.CLOSED: 'secondary',
            self.Status.DEFAULTED: 'danger',
        }
        return status_colors.get(self.status, 'secondary')

    def get_risk_level_color(self):
        """Get the Bootstrap color class for the current risk level."""
        risk_colors = {
            self.RiskLevel.LOW: 'success',
            self.RiskLevel.MODERATE: 'info',
            self.RiskLevel.MEDIUM: 'warning',
            self.RiskLevel.HIGH: 'danger',
        }
        return risk_colors.get(self.risk_level, 'secondary')

    def generate_repayment_schedule(self):
        """Generate repayment schedule for the loan."""
        # Clear existing schedule
        self.repayment_schedule.all().delete()

        if not self.disbursement_date:
            return

        # Calculate monthly payment using PMT formula
        monthly_rate = self.interest_rate / 12 / 100
        monthly_payment = -1 * npf.pmt(monthly_rate, self.term_months, self.amount)

        # Generate schedule
        current_date = self.disbursement_date
        remaining_principal = self.amount

        for installment in range(1, self.term_months + 1):
            interest_payment = remaining_principal * monthly_rate
            principal_payment = monthly_payment - interest_payment
            remaining_principal -= principal_payment

            RepaymentSchedule.objects.create(
                loan=self,
                installment_number=installment,
                due_date=current_date + timedelta(days=30 * installment),
                principal_amount=principal_payment,
                interest_amount=interest_payment,
                total_amount=monthly_payment
            )

    def save(self, *args, **kwargs):
        """Override save to handle status transitions and related actions."""
        if not self.application_number:
            # Generate application number
            year = timezone.now().year
            count = Loan.objects.filter(
                application_date__year=year
            ).count() + 1
            self.application_number = f"L{year}{count:06d}"

        # Handle status transitions
        if self.status == self.Status.APPROVED and not self.approval_date:
            self.approval_date = timezone.now()
        elif self.status == self.Status.DISBURSED and not self.disbursement_date:
            self.disbursement_date = timezone.now()
            # Calculate maturity date
            self.maturity_date = self.disbursement_date + timedelta(days=30 * self.term_months)

        super().save(*args, **kwargs)

        # Generate repayment schedule if disbursed
        if self.status == self.Status.DISBURSED:
            self.generate_repayment_schedule()


class RiskAlert(models.Model):
    """Model for risk-related alerts."""
    
    class AlertType(models.TextChoices):
        HIGH_RISK_APPLICATION = 'HIGH_RISK', _('High Risk Application')
        MULTIPLE_ACTIVE_LOANS = 'MULTIPLE_LOANS', _('Multiple Active Loans')
        PAYMENT_PATTERN = 'PAYMENT_PATTERN', _('Suspicious Payment Pattern')
        RAPID_REQUESTS = 'RAPID_REQUESTS', _('Rapid Loan Requests')
        AMOUNT_SPIKE = 'AMOUNT_SPIKE', _('Unusual Amount Increase')
    
    class Severity(models.TextChoices):
        LOW = 'LOW', _('Low')
        MEDIUM = 'MEDIUM', _('Medium')
        HIGH = 'HIGH', _('High')
        CRITICAL = 'CRITICAL', _('Critical')
    
    loan = models.ForeignKey(
        'Loan',
        on_delete=models.CASCADE,
        related_name='risk_alerts'
    )
    alert_type = models.CharField(
        max_length=20,
        choices=AlertType.choices
    )
    severity = models.CharField(
        max_length=10,
        choices=Severity.choices
    )
    message = models.TextField()
    details = models.JSONField(
        null=True,
        blank=True,
        help_text=_('Additional alert details in JSON format')
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_('Whether this alert is still active')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_alerts'
    )
    resolution_notes = models.TextField(
        null=True,
        blank=True,
        help_text=_('Notes about how the alert was resolved')
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['loan', 'alert_type', 'is_active']),
            models.Index(fields=['created_at', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.get_alert_type_display()} - {self.loan}"
    
    def resolve(self, user, notes=None):
        """Mark the alert as resolved."""
        self.is_active = False
        self.resolved_at = timezone.now()
        self.resolved_by = user
        if notes:
            self.resolution_notes = notes
        self.save()


class LoanDocument(models.Model):
    """Model for loan-related documents."""
    
    class DocumentType(models.TextChoices):
        APPLICATION = 'APPLICATION', _('Loan Application')
        AGREEMENT = 'AGREEMENT', _('Loan Agreement')
        COLLATERAL = 'COLLATERAL', _('Collateral Document')
        OTHER = 'OTHER', _('Other')
    
    loan = models.ForeignKey(
        Loan,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    document_type = models.CharField(
        max_length=20,
        choices=DocumentType.choices
    )
    document_path = models.CharField(max_length=255)
    description = models.CharField(max_length=200)
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='uploaded_loan_documents'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('loan document')
        verbose_name_plural = _('loan documents')
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.loan.application_number} - {self.get_document_type_display()}"


class RepaymentSchedule(models.Model):
    """Model for loan repayment schedules."""
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        PARTIALLY_PAID = 'PARTIALLY_PAID', _('Partially Paid')
        PAID = 'PAID', _('Paid')
        OVERDUE = 'OVERDUE', _('Overdue')
    
    loan = models.ForeignKey(
        'Loan',
        on_delete=models.CASCADE,
        related_name='repayment_schedule'
    )
    installment_number = models.IntegerField()
    due_date = models.DateField()
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
        validators=[MinValueValidator(0)],
        default=0
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    paid_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    paid_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['due_date', 'installment_number']
        unique_together = ['loan', 'installment_number']
    
    def __str__(self):
        return f"{self.loan.reference_number} - Installment {self.installment_number}"
    
    @property
    def remaining_amount(self):
        """Calculate remaining amount to be paid."""
        return self.total_amount - self.paid_amount
    
    @property
    def is_overdue(self):
        """Check if payment is overdue."""
        return (
            self.status != self.Status.PAID and
            self.due_date < timezone.now().date()
        )
    
    def update_status(self):
        """Update payment status based on amounts and due date."""
        if self.paid_amount >= self.total_amount:
            self.status = self.Status.PAID
        elif self.paid_amount > 0:
            self.status = self.Status.PARTIALLY_PAID
        elif self.is_overdue:
            self.status = self.Status.OVERDUE
        else:
            self.status = self.Status.PENDING
        self.save()


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
        'Loan',
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    repayment_schedule = models.ForeignKey(
        'RepaymentSchedule',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transactions'
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
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_transactions'
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
        return f"{self.reference_number} - {self.get_transaction_type_display()}"
    
    def save(self, *args, **kwargs):
        if not self.reference_number:
            self.reference_number = f"TXN-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
        
    def complete_transaction(self, user):
        """Mark transaction as completed and update related records."""
        self.status = self.Status.COMPLETED
        self.processed_by = user
        self.processed_at = timezone.now()
        self.save()
        
        if self.transaction_type == self.Type.REPAYMENT and self.repayment_schedule:
            self.repayment_schedule.paid_amount += self.amount
            self.repayment_schedule.paid_date = timezone.now().date()
            self.repayment_schedule.save()
            self.repayment_schedule.update_status()
            
        elif self.transaction_type == self.Type.DISBURSEMENT:
            self.loan.disbursed_amount = self.amount
            self.loan.disbursement_date = timezone.now().date()
            self.loan.status = Loan.Status.DISBURSED
            self.loan.save()
    
    def reverse_transaction(self, user, notes=None):
        """Reverse a completed transaction."""
        if self.status != self.Status.COMPLETED:
            raise ValueError("Only completed transactions can be reversed")
            
        self.status = self.Status.REVERSED
        self.processed_by = user
        self.processed_at = timezone.now()
        if notes:
            self.notes = f"{self.notes}\nReversed: {notes}" if self.notes else f"Reversed: {notes}"
        self.save()
        
        if self.transaction_type == self.Type.REPAYMENT and self.repayment_schedule:
            self.repayment_schedule.paid_amount -= self.amount
            self.repayment_schedule.save()
            self.repayment_schedule.update_status()
            
        elif self.transaction_type == self.Type.DISBURSEMENT:
            self.loan.disbursed_amount = 0
            self.loan.disbursement_date = None
            self.loan.status = Loan.Status.APPROVED
            self.loan.save()
