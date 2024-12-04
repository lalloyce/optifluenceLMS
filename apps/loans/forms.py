from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .models import Loan, LoanDocument
from .services.risk_assessment import LoanRiskAssessment
from decimal import Decimal
from .models import Customer

class LoanApplicationForm(forms.ModelForm):
    """Form for loan applications."""
    
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
            from .services.risk_assessment import LoanRiskAssessment
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
        
        # Set interest rate and processing fee from loan product
        loan.interest_rate = loan_product.interest_rate
        loan.processing_fee = (loan_product.processing_fee / 100) * loan.amount
        
        # Store risk assessment results
        if hasattr(self, 'risk_assessment'):
            loan.risk_score = self.risk_assessment.score
            loan.risk_factors = self.risk_assessment.risk_factors
            
            # Set initial status based on auto-approval threshold
            if loan.risk_score >= loan_product.auto_approve_above:
                loan.status = Loan.Status.APPROVED
                loan.approval_date = timezone.now()
            
        if commit:
            loan.save()
            
            # Create risk alerts
            from .services.risk_alerts import RiskAlertService
            alert_service = RiskAlertService(loan)
            alert_service.check_all_risk_patterns()
            
        return loan


class LoanApprovalForm(forms.Form):
    """Form for loan approval."""
    
    notes = forms.CharField(
        widget=forms.Textarea,
        required=False,
        help_text=_('Add any notes regarding the loan approval decision.')
    )


class LoanDocumentForm(forms.ModelForm):
    """Form for uploading loan documents."""
    
    class Meta:
        model = LoanDocument
        fields = ['document_type', 'document_path', 'description']
        widgets = {
            'description': forms.TextInput(attrs={'placeholder': _('Brief description of the document')}),
        }
    
    def clean_document_path(self):
        document = self.cleaned_data.get('document_path')
        if document:
            # Validate file size (max 5MB)
            if document.size > 5 * 1024 * 1024:
                raise ValidationError(_('File size cannot exceed 5MB.'))
            
            # Validate file extension
            allowed_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
            ext = document.name.lower().split('.')[-1]
            if f'.{ext}' not in allowed_extensions:
                raise ValidationError(_('Invalid file type. Allowed types: PDF, DOC, DOCX, JPG, PNG'))
        
        return document
