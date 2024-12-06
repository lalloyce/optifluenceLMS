from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.customers.models import Customer
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import uuid
from .config import LoanConfig


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
        help_text=_('Maximum amount for high-risk loans (score < 40)')
    )
    medium_risk_max_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text=_('Maximum amount for medium-risk loans (score 40-59)')
    )
    moderate_risk_max_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
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


class LoanApplication(models.Model):
    """Model for loan applications before they become actual loans."""
    
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', _('Draft')
        SUBMITTED = 'SUBMITTED', _('Submitted')
        IN_REVIEW = 'IN_REVIEW', _('In Review')
        APPROVED = 'APPROVED', _('Approved')
        REJECTED = 'REJECTED', _('Rejected')
        CANCELLED = 'CANCELLED', _('Cancelled')
    
    class EmploymentStatus(models.TextChoices):
        EMPLOYED = 'EMPLOYED', _('Employed')
        SELF_EMPLOYED = 'SELF_EMPLOYED', _('Self Employed')
        BUSINESS_OWNER = 'BUSINESS_OWNER', _('Business Owner')
        UNEMPLOYED = 'UNEMPLOYED', _('Unemployed')
        RETIRED = 'RETIRED', _('Retired')
        STUDENT = 'STUDENT', _('Student')
    
    application_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='loan_applications'
    )
    loan_product = models.ForeignKey(
        LoanProduct,
        on_delete=models.PROTECT,
        related_name='applications'
    )
    amount_requested = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    term_months = models.IntegerField(validators=[MinValueValidator(1)])
    purpose = models.TextField()
    
    # Employment and Income Information
    employment_status = models.CharField(
        max_length=20,
        choices=EmploymentStatus.choices,
        help_text=_('Current employment status')
    )
    monthly_income = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text=_('Monthly income in base currency')
    )
    other_loans = models.TextField(
        blank=True,
        help_text=_('Details of other active loans or financial commitments')
    )
    
    # Application Status
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )
    submitted_date = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_applications'
    )
    review_date = models.DateTimeField(null=True, blank=True)
    
    # Supporting Documents
    documents = models.JSONField(
        null=True,
        blank=True,
        help_text=_('List of supporting documents')
    )
    
    # Additional Information
    notes = models.TextField(null=True, blank=True)
    rejection_reason = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('loan application')
        verbose_name_plural = _('loan applications')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Application {self.application_number} - {self.customer.full_name}"
    
    def save(self, *args, **kwargs):
        if not self.application_number:
            self.application_number = f"APP{timezone.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)
    
    def submit(self):
        """Submit the application for review."""
        if self.status == self.Status.DRAFT:
            self.status = self.Status.SUBMITTED
            self.submitted_date = timezone.now()
            self.save()
    
    def start_review(self, reviewer):
        """Start the review process."""
        if self.status == self.Status.SUBMITTED:
            self.status = self.Status.IN_REVIEW
            self.reviewed_by = reviewer
            self.review_date = timezone.now()
            self.save()
    
    def approve(self):
        """Approve the application."""
        if self.status in [self.Status.SUBMITTED, self.Status.IN_REVIEW]:
            self.status = self.Status.APPROVED
            self.save()
    
    def reject(self, reason):
        """Reject the application."""
        if self.status in [self.Status.SUBMITTED, self.Status.IN_REVIEW]:
            self.status = self.Status.REJECTED
            self.rejection_reason = reason
            self.save()
    
    def cancel(self):
        """Cancel the application."""
        if self.status in [self.Status.DRAFT, self.Status.SUBMITTED]:
            self.status = self.Status.CANCELLED
            self.save()


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
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='handled_loans'
    )
    application = models.OneToOneField(
        LoanApplication,
        on_delete=models.PROTECT,
        related_name='loan',
        null=True,
        blank=True
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
        return f"Loan {self.application_number} - {self.customer.full_name}"
    
    def save(self, *args, **kwargs):
        if not self.application_number:
            self.application_number = f"LN{timezone.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)
        
    def generate_repayment_schedule(self):
        """Generate repayment schedule for the loan."""
        from .repayment import RepaymentSchedule
        
        if self.status != self.Status.DISBURSED:
            raise ValueError("Cannot generate repayment schedule for non-disbursed loan")
            
        # Calculate monthly payment using PMT formula
        monthly_rate = self.interest_rate / 12 / 100
        monthly_payment = (self.amount * monthly_rate * (1 + monthly_rate) ** self.term_months) / ((1 + monthly_rate) ** self.term_months - 1)
        
        remaining_principal = self.amount
        payment_date = self.disbursement_date
        
        for installment in range(1, self.term_months + 1):
            payment_date = payment_date + timedelta(days=30)
            interest_payment = remaining_principal * monthly_rate
            principal_payment = monthly_payment - interest_payment
            
            if installment == self.term_months:
                # Adjust last payment to account for rounding errors
                principal_payment = remaining_principal
                
            RepaymentSchedule.objects.create(
                loan=self,
                installment_number=installment,
                due_date=payment_date.date(),
                principal_amount=principal_payment,
                interest_amount=interest_payment,
                total_amount=principal_payment + interest_payment
            )
            
            remaining_principal -= principal_payment
    
    def update_risk_level(self):
        """Update risk level based on risk score."""
        if self.risk_score is None:
            return
            
        if self.risk_score >= 80:
            self.risk_level = self.RiskLevel.LOW
        elif self.risk_score >= 60:
            self.risk_level = self.RiskLevel.MODERATE
        elif self.risk_score >= 40:
            self.risk_level = self.RiskLevel.MEDIUM
        else:
            self.risk_level = self.RiskLevel.HIGH
        self.save()
    
    @classmethod
    def create_from_application(cls, application, loan_officer):
        """Create a new loan from an approved application."""
        if application.status != LoanApplication.Status.APPROVED:
            raise ValueError("Can only create loan from approved application")
            
        loan = cls.objects.create(
            loan_product=application.loan_product,
            customer=application.customer,
            loan_officer=loan_officer,
            application=application,
            amount=application.amount_requested,
            term_months=application.term_months,
            interest_rate=application.loan_product.interest_rate,
            processing_fee=application.loan_product.processing_fee,
            purpose=application.purpose,
            status=cls.Status.PENDING
        )
        return loan
