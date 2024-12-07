from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .models import Loan, LoanProduct
from apps.customers.models import Customer
from .services.risk_assessment import LoanRiskAssessment
from decimal import Decimal

class LoanForm(forms.ModelForm):
    """Form for loans."""
    
    class Meta:
        model = Loan
        fields = [
            'loan_product',
            'customer',
            'amount',
            'term_months',
            'purpose',
        ]
        widgets = {
            'purpose': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
