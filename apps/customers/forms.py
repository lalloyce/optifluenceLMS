from django import forms
from django.core.exceptions import ValidationError
from .models import Customer, BusinessProfile
import re

class CustomerBasicForm(forms.ModelForm):
    """First step of customer creation - basic information."""
    
    class Meta:
        model = Customer
        fields = [
            'first_name',
            'last_name',
            'email',
            'phone_number',
            'customer_type'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'customer_type': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_phone_number(self):
        """Validate phone number format."""
        phone = self.cleaned_data.get('phone_number')
        if phone:
            # Remove any spaces or special characters
            phone = ''.join(filter(str.isdigit, phone))
            # Ensure it starts with country code or add it
            if not phone.startswith('+'):
                phone = '+' + phone
        return phone

    def clean_email(self):
        """Validate email is unique if provided."""
        email = self.cleaned_data.get('email')
        if email:
            if Customer.objects.filter(email=email).exists():
                raise ValidationError("This email is already registered.")
        return email

class CustomerAddressForm(forms.ModelForm):
    """Second step of customer creation - address information."""
    
    city = forms.CharField(max_length=100)
    
    class Meta:
        model = Customer
        fields = [
            'address',
            'city',
            'postal_code',
            'country'
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
        }

class CustomerIdentityForm(forms.ModelForm):
    """Third step of customer creation - identity information."""
    
    ID_TYPE_CHOICES = [
        ('passport', 'Passport'),
        ('national_id', 'National ID'),
        ('drivers_license', 'Driver\'s License'),
    ]
    
    id_type = forms.ChoiceField(choices=ID_TYPE_CHOICES)
    id_number = forms.CharField(max_length=20)

    def clean_id_number(self):
        id_type = self.cleaned_data.get('id_type')
        id_number = self.cleaned_data.get('id_number')

        if not id_number:
            raise forms.ValidationError("ID number is required")

        if id_type == 'national_id':
            if not (id_number.isdigit() and len(id_number) == 8):
                raise forms.ValidationError("National ID must be 8 digits")
        elif id_type in ['passport', 'drivers_license']:
            if not re.match(r'^[A-Za-z0-9]{6,20}$', id_number):
                raise forms.ValidationError("ID must be 6-20 alphanumeric characters")

        return id_number

    class Meta:
        model = Customer
        fields = [
            'id_type',
            'id_number'
        ]
        widgets = {
            'id_type': forms.Select(attrs={'class': 'form-control'}),
            'id_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

class CustomerEmploymentForm(forms.ModelForm):
    """Fourth step of customer creation - employment information."""
    
    class Meta:
        model = Customer
        fields = [
            'employer',
            'occupation',
            'monthly_income'
        ]
        widgets = {
            'employer': forms.TextInput(attrs={'class': 'form-control'}),
            'occupation': forms.TextInput(attrs={'class': 'form-control'}),
            'monthly_income': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class BusinessProfileForm(forms.ModelForm):
    """Additional form for business customers."""
    
    class Meta:
        model = BusinessProfile
        fields = [
            'business_name',
            'registration_number',
            'business_type',
            'annual_revenue'
        ]
        widgets = {
            'business_name': forms.TextInput(attrs={'class': 'form-control'}),
            'registration_number': forms.TextInput(attrs={'class': 'form-control'}),
            'business_type': forms.Select(attrs={'class': 'form-control'}),
            'annual_revenue': forms.NumberInput(attrs={'class': 'form-control'}),
        }
