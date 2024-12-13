from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.customers.models import Customer
from .loan_product import LoanProduct

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
