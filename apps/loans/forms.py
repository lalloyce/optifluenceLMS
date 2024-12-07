from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .models import Loan, LoanProduct, LoanApplication
from apps.customers.models import Customer
from .services.risk_assessment import LoanRiskAssessment
from decimal import Decimal

class LoanForm(forms.ModelForm):
    """Form for loans."""
    
    guarantor = forms.ModelChoiceField(
        queryset=Customer.objects.all(),
        required=False,
        empty_label="Select a guarantor (optional)"
    )
    
    class Meta:
        model = Loan
        fields = [
            'loan_product',
            'customer',
            'amount',
            'term_months',
            'purpose',
            'guarantor',
            'disbursement_date',
        ]
        widgets = {
            'purpose': forms.Textarea(attrs={'rows': 3}),
            'disbursement_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['loan_product'].queryset = LoanProduct.objects.filter(is_active=True)
        self.fields['loan_product'].empty_label = "Select a loan product"
        self.fields['customer'].empty_label = "Select a customer"
        self.risk_assessment = None
        
        if self.is_bound and self.data.get('customer') and self.data.get('amount'):
            try:
                customer = Customer.objects.get(pk=self.data['customer'])
                amount = Decimal(self.data['amount'])
                self.risk_assessment = LoanRiskAssessment(customer, amount)
                self.risk_summary = self.risk_assessment.get_risk_assessment_summary()
            except (Customer.DoesNotExist, ValueError):
                pass
    
    def clean(self):
        cleaned_data = super().clean()
        loan_product = cleaned_data.get('loan_product')
        amount = cleaned_data.get('amount')
        term_months = cleaned_data.get('term_months')
        customer = cleaned_data.get('customer')
        disbursement_date = cleaned_data.get('disbursement_date')
        
        if all([loan_product, amount, term_months, customer]):
            # Perform risk assessment
            risk_assessment = LoanRiskAssessment(customer, amount)
            risk_score = risk_assessment.calculate_risk_score()
            
            # Store risk assessment for the view
            self.risk_assessment = risk_assessment
            
            # Check risk-based amount limits
            max_allowed = loan_product.get_max_amount_for_risk_score(risk_score)
            if amount > max_allowed:
                raise ValidationError(
                    _('Based on the risk assessment, the maximum allowed amount is %(max_amount)s'),
                    params={'max_amount': max_allowed},
                )
            
            # Check automatic rejection threshold
            if risk_score < loan_product.auto_reject_below:
                raise ValidationError(
                    _('This application cannot proceed due to high risk score (%(score)s)'),
                    params={'score': risk_score},
                )
            
            # Validate loan product limits
            if amount < loan_product.minimum_amount:
                raise ValidationError(
                    _('Loan amount cannot be less than %(min_amount)s'),
                    params={'min_amount': loan_product.minimum_amount},
                )
            if amount > loan_product.maximum_amount:
                raise ValidationError(
                    _('Loan amount cannot exceed %(max_amount)s'),
                    params={'max_amount': loan_product.maximum_amount},
                )
            
            if term_months < loan_product.minimum_term:
                raise ValidationError(
                    _('Loan term cannot be less than %(min_term)s months'),
                    params={'min_term': loan_product.minimum_term},
                )
            if term_months > loan_product.maximum_term:
                raise ValidationError(
                    _('Loan term cannot exceed %(max_term)s months'),
                    params={'max_term': loan_product.maximum_term},
                )
            
        if disbursement_date and disbursement_date < timezone.now().date():
            raise ValidationError({
                'disbursement_date': _('Disbursement date cannot be in the past.')
            })
        
        return cleaned_data
    
    def save(self, commit=True):
        loan = super().save(commit=False)
        loan_product = loan.loan_product
        
        # Store risk assessment results
        if hasattr(self, 'risk_assessment'):
            loan.risk_score = self.risk_assessment.score
            loan.risk_factors = self.risk_assessment.risk_factors
            
            # Set initial status based on auto-approval threshold
            if loan.risk_score >= loan_product.auto_approve_above:
                loan.status = Loan.Status.AUTO_APPROVED
                loan.decision_date = timezone.now()
            
        if commit:
            loan.save()
            
            # Create risk alerts
            from .services.risk_alerts import RiskAlertService
            alert_service = RiskAlertService(loan)
            alert_service.check_all_risk_patterns()
            
        return loan


class LoanApplicationForm(forms.ModelForm):
    """Form for loan applications."""
    
    customer = forms.ModelChoiceField(
        queryset=Customer.objects.filter(is_active=True),
        empty_label="Select a customer",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = LoanApplication
        fields = [
            'customer',
            'loan_product',
            'amount_requested',
            'term_months',
            'purpose',
            'employment_status',
            'monthly_income',
            'other_loans',
            'disbursement_date'
        ]
        widgets = {
            'purpose': forms.Textarea(attrs={'rows': 3}),
            'other_loans': forms.Textarea(attrs={'rows': 2}),
            'disbursement_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'term_months': forms.NumberInput(attrs={
                'class': 'form-control',
                'readonly': 'readonly'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['loan_product'].queryset = LoanProduct.objects.filter(is_active=True)
        self.fields['loan_product'].empty_label = "Select a loan product"
        
        # Add help texts
        self.fields['customer'].help_text = "Select the customer applying for the loan"
        self.fields['amount_requested'].help_text = "Enter the amount to borrow"
        self.fields['term_months'].help_text = "Loan term is set by the selected product"
        self.fields['monthly_income'].help_text = "Customer's total monthly income"
        self.fields['disbursement_date'].help_text = "When should the loan be disbursed?"
        
        # If we have a loan product selected, set the term_months
        if self.data.get('loan_product'):
            try:
                product = LoanProduct.objects.get(pk=self.data['loan_product'])
                self.initial['term_months'] = product.term_months
            except (LoanProduct.DoesNotExist, ValueError):
                pass


class LoanApprovalForm(forms.Form):
    """Form for loan approval."""
    
    decision = forms.ChoiceField(
        choices=Loan.Status.choices,
        required=True,
        help_text=_('Select the approval decision for this loan.')
    )
    
    approved_amount = forms.DecimalField(
        required=False,
        help_text=_('If approved, specify the approved loan amount.')
    )
    
    interest_rate = forms.DecimalField(
        required=False,
        help_text=_('If approved, specify the interest rate.')
    )
    
    notes = forms.CharField(
        widget=forms.Textarea,
        required=False,
        help_text=_('Add any notes regarding the loan approval decision.')
    )
    
    def clean(self):
        cleaned_data = super().clean()
        decision = cleaned_data.get('decision')
        approved_amount = cleaned_data.get('approved_amount')
        interest_rate = cleaned_data.get('interest_rate')
        
        if decision == Loan.Status.APPROVED:
            if not approved_amount:
                raise ValidationError(_('Approved amount is required for approved loans.'))
            if not interest_rate:
                raise ValidationError(_('Interest rate is required for approved loans.'))
        
        return cleaned_data
