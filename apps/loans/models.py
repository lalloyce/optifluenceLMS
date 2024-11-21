from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.customers.models import Customer
from apps.accounts.models import User


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
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('loan product')
        verbose_name_plural = _('loan products')
    
    def __str__(self):
        return self.name


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
