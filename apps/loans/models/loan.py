from decimal import Decimal
from dateutil.relativedelta import relativedelta
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.customers.models import Customer
from django.conf import settings
from django.utils import timezone
from .repayment import RepaymentSchedule
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
    
    # Loan terms and fees
    term_months = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text=_('Default term length in months'),
        default=1  # Default 1 month term
    )
    grace_period_months = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text=_('Grace period in months before first payment is due')
    )
    penalty_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_('Annual penalty rate for late payments'),
        default=Decimal('10.00')  # Default 10% annual penalty rate
    )
    insurance_fee = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_('Insurance fee as percentage of loan amount'),
        default=Decimal('0.00')  # Default 0% insurance fee
    )
    
    # Documentation and eligibility
    required_documents = models.JSONField(
        null=True,
        blank=True,
        help_text=_('List of required documents for loan application')
    )
    eligibility_criteria = models.JSONField(
        null=True,
        blank=True,
        help_text=_('Eligibility criteria for loan approval')
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
    purpose = models.TextField(null=True, blank=True)
    
    # Employment and Income Information
    employment_status = models.CharField(
        max_length=20,
        choices=EmploymentStatus.choices,
        help_text=_('Current employment status'),
        null=True,
        blank=True
    )
    monthly_income = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text=_('Monthly income in base currency'),
        null=True,
        blank=True
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
    disbursement_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('Requested date for loan disbursement')
    )
    
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
        if self.status not in [self.Status.SUBMITTED, self.Status.IN_REVIEW]:
            raise ValueError("Can only approve submitted or in-review applications")
        
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
    purpose = models.TextField(null=True, blank=True)
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
        if not self.disbursement_date:
            raise ValueError("Cannot generate schedule without disbursement date")
            
        # Delete existing schedule if any
        RepaymentSchedule.objects.filter(loan=self).delete()
        
        # Calculate amounts
        principal_per_installment = self.amount / self.term_months
        
        # Calculate total interest using simple interest
        annual_rate = self.interest_rate / Decimal('100')
        term_years = self.term_months / Decimal('12')
        total_interest = self.amount * annual_rate * term_years
        interest_per_installment = total_interest / self.term_months
        
        # Generate schedule
        for i in range(self.term_months):
            due_date = (self.disbursement_date + relativedelta(months=i + 1)).date()
            
            RepaymentSchedule.objects.create(
                loan=self,
                installment_number=i + 1,
                due_date=due_date,
                principal_amount=principal_per_installment,
                interest_amount=interest_per_installment,
                total_amount=principal_per_installment + interest_per_installment,
                penalty_amount=Decimal('0.00'),
                status=RepaymentSchedule.Status.PENDING
            )
    
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
            
        # Set disbursement date to today if not specified
        if not application.disbursement_date:
            application.disbursement_date = timezone.now()
            application.save()
            
        loan = cls.objects.create(
            loan_product=application.loan_product,
            customer=application.customer,
            loan_officer=loan_officer,
            application=application,
            application_number=application.application_number,
            amount=application.amount_requested,
            term_months=application.term_months,
            interest_rate=application.loan_product.interest_rate,
            processing_fee=application.loan_product.processing_fee,
            risk_score=getattr(application, 'risk_score', None),
            risk_level=getattr(application, 'risk_level', None),
            risk_factors=getattr(application, 'risk_factors', None),
            risk_notes=getattr(application, 'risk_notes', None),
            purpose=application.purpose,
            disbursement_date=application.disbursement_date,
            status=cls.Status.APPROVED
        )
        
        # Generate initial repayment schedule
        loan.generate_repayment_schedule()
        
        return loan
