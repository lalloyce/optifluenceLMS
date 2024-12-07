from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.accounts.models import User


class Customer(models.Model):
    """Customer model for loan management."""
    
    class Gender(models.TextChoices):
        MALE = 'MALE', _('Male')
        FEMALE = 'FEMALE', _('Female')
        OTHER = 'OTHER', _('Other')
    
    class CustomerType(models.TextChoices):
        INDIVIDUAL = 'INDIVIDUAL', _('Individual')
        BUSINESS = 'BUSINESS', _('Business')
    
    class VerificationStatus(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        VERIFIED = 'VERIFIED', _('Verified')
        REJECTED = 'REJECTED', _('Rejected')
    
    # Required Fields
    first_name = models.CharField(max_length=100, default='')
    last_name = models.CharField(max_length=100, default='')
    phone_number = models.CharField(max_length=20, default='')
    email = models.EmailField(unique=True, null=True, blank=True)
    profile_picture = models.ImageField(
        upload_to='customers/profile_pictures/%Y/%m/',
        null=True,
        blank=True,
        help_text='Upload a profile picture (optional)'
    )
    customer_type = models.CharField(
        max_length=20,
        choices=CustomerType.choices,
        default=CustomerType.INDIVIDUAL
    )
    gender = models.CharField(
        max_length=10,
        choices=Gender.choices,
        default=Gender.MALE,
        null=False,
        blank=False
    )
    is_active = models.BooleanField(default=True)
    
    # Optional Fields
    date_of_birth = models.DateField(null=True, blank=True)
    
    # Address Information (Optional)
    address = models.TextField(default='')
    city = models.CharField(max_length=100, default='')
    state = models.CharField(max_length=100, default='')
    postal_code = models.CharField(max_length=20, default='')
    country = models.CharField(max_length=100, default='')
    
    # Identity Information (Optional)
    id_type = models.CharField(max_length=50, default='')
    id_number = models.CharField(max_length=100, default='')
    id_expiry_date = models.DateField(null=True, blank=True)
    
    # Verification Information (Optional)
    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING
    )
    verification_notes = models.TextField(null=True, blank=True)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_customers'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Employment Information (Optional)
    employer = models.CharField(max_length=100, null=True, blank=True, default='')
    occupation = models.CharField(max_length=100, null=True, blank=True, default='')
    monthly_income = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        null=True,
        blank=True
    )
    employment_duration = models.IntegerField(null=True, blank=True)
    
    # Risk Assessment (Optional)
    credit_score = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(300), MaxValueValidator(850)]
    )
    risk_rating = models.CharField(max_length=20, null=True, blank=True)
    
    # Recommendation System (Optional)
    recommendation_score = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    last_recommendation_date = models.DateTimeField(null=True, blank=True)
    recommended_products = models.JSONField(null=True, blank=True)
    
    # Meta Information
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_customers'
    )
    
    class Meta:
        verbose_name = _('customer')
        verbose_name_plural = _('customers')
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['id_number']),
            models.Index(fields=['customer_type', 'is_active']),
        ]
        unique_together = ['id_type', 'id_number']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_customer_type_display()})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_initials(self):
        return f"{self.first_name[0]}{self.last_name[0]}".upper()

    @property
    def is_business(self):
        return self.customer_type == self.CustomerType.BUSINESS

    def get_active_loans(self):
        return self.loans.filter(status='DISBURSED')

    def get_loan_history(self):
        return self.loans.all().order_by('-created_at')

    def get_total_loan_amount(self):
        return sum(loan.amount for loan in self.loans.all())

    def get_total_outstanding_amount(self):
        return sum(loan.get_outstanding_amount() for loan in self.get_active_loans())


class BusinessProfile(models.Model):
    """Business profile for business customers."""
    
    class BusinessType(models.TextChoices):
        SOLE_PROPRIETORSHIP = 'SOLE_PROPRIETORSHIP', _('Sole Proprietorship')
        PARTNERSHIP = 'PARTNERSHIP', _('Partnership')
        CORPORATION = 'CORPORATION', _('Corporation')
        LLC = 'LLC', _('Limited Liability Company')
        OTHER = 'OTHER', _('Other')
    
    # Link to Customer
    customer = models.OneToOneField(
        Customer,
        on_delete=models.CASCADE,
        related_name='business_profile'
    )
    
    # Required Fields
    business_name = models.CharField(max_length=255)
    business_type = models.CharField(
        max_length=50,
        choices=BusinessType.choices
    )
    primary_contact_name = models.CharField(max_length=255)
    primary_contact_position = models.CharField(max_length=100)
    primary_contact_phone = models.CharField(max_length=20)
    
    # Optional Fields
    registration_number = models.CharField(max_length=100, unique=True, null=True, blank=True)
    tax_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    incorporation_date = models.DateField(null=True, blank=True)
    industry = models.CharField(max_length=100, null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    
    # Business Financials (Optional)
    annual_revenue = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True
    )
    number_of_employees = models.IntegerField(null=True, blank=True)
    years_in_business = models.IntegerField(null=True, blank=True)
    
    # Additional Contact Information (Optional)
    primary_contact_email = models.EmailField(null=True, blank=True)
    
    # Additional Information
    business_description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('business profile')
        verbose_name_plural = _('business profiles')
        indexes = [
            models.Index(fields=['business_name', 'business_type']),
            models.Index(fields=['primary_contact_name', 'primary_contact_phone']),
        ]
    
    def __str__(self):
        return self.business_name


class CustomerDocument(models.Model):
    """Model for customer-related documents."""
    
    class DocumentType(models.TextChoices):
        ID_PROOF = 'ID_PROOF', _('ID Proof')
        ADDRESS_PROOF = 'ADDRESS_PROOF', _('Address Proof')
        INCOME_PROOF = 'INCOME_PROOF', _('Income Proof')
        BUSINESS_REGISTRATION = 'BUSINESS_REGISTRATION', _('Business Registration')
        TAX_DOCUMENT = 'TAX_DOCUMENT', _('Tax Document')
        OTHER = 'OTHER', _('Other')
    
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    document_type = models.CharField(
        max_length=50,
        choices=DocumentType.choices
    )
    document_path = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_customer_documents'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='verified_customer_documents'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    verification_notes = models.TextField(null=True, blank=True)
    
    class Meta:
        verbose_name = _('customer document')
        verbose_name_plural = _('customer documents')
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.customer.get_full_name()} - {self.document_type}"
