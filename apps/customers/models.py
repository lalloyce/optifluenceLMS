from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.accounts.models import User


class Customer(models.Model):
    """Customer model for loan management."""
    
    class Gender(models.TextChoices):
        MALE = 'MALE', _('Male')
        FEMALE = 'FEMALE', _('Female')
        OTHER = 'OTHER', _('Other')
    
    # Personal Information
    full_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    gender = models.CharField(
        max_length=10,
        choices=Gender.choices
    )
    email = models.EmailField(unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=20)
    address = models.TextField()
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    
    # Identity Information
    id_type = models.CharField(max_length=50)
    id_number = models.CharField(max_length=100)
    id_expiry_date = models.DateField(null=True, blank=True)
    
    # Employment Information
    employment_status = models.CharField(max_length=50)
    employer_name = models.CharField(max_length=255, null=True, blank=True)
    employer_address = models.TextField(null=True, blank=True)
    employer_phone = models.CharField(max_length=20, null=True, blank=True)
    monthly_income = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    employment_duration = models.IntegerField(null=True, blank=True)
    
    # Additional Information
    credit_score = models.IntegerField(null=True, blank=True)
    risk_rating = models.CharField(max_length=20, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        verbose_name = _('customer')
        verbose_name_plural = _('customers')
        unique_together = ['id_type', 'id_number']
    
    def __str__(self):
        return self.full_name


class CustomerDocument(models.Model):
    """Model for customer-related documents."""
    
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    document_type = models.CharField(max_length=50)
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
    
    class Meta:
        verbose_name = _('customer document')
        verbose_name_plural = _('customer documents')
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.customer.full_name} - {self.document_type}"
