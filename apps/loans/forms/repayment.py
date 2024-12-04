from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from decimal import Decimal

from ..models import Transaction, Loan
from ..services.repayment import RepaymentService

class RepaymentForm(forms.ModelForm):
    """Form for processing loan repayments."""
    
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.01'),
        widget=forms.NumberInput(attrs={'step': '0.01'})
    )
    payment_method = forms.ChoiceField(
        choices=[
            ('CASH', _('Cash')),
            ('BANK_TRANSFER', _('Bank Transfer')),
            ('CHECK', _('Check')),
            ('MOBILE_MONEY', _('Mobile Money')),
        ]
    )
    reference = forms.CharField(
        max_length=50,
        required=False,
        help_text=_('External payment reference (e.g., bank transfer reference)')
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False
    )

    class Meta:
        model = Transaction
        fields = ['amount', 'payment_method', 'reference', 'notes']

    def __init__(self, *args, **kwargs):
        self.loan = kwargs.pop('loan')
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        
        # Get loan balance
        repayment_service = RepaymentService(self.loan)
        balance = repayment_service.get_loan_balance()
        
        # Update amount field with current balance
        self.fields['amount'].widget.attrs.update({
            'max': balance['total_balance'],
            'data-balance': balance['total_balance'],
            'data-penalties': balance['penalties']
        })
        
        # Add balance information to form
        self.balance_info = balance

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise ValidationError(_('Payment amount must be greater than zero'))
            
        repayment_service = RepaymentService(self.loan)
        balance = repayment_service.get_loan_balance()
        
        if amount > balance['total_balance']:
            raise ValidationError(
                _('Payment amount (%(amount)s) cannot exceed total balance (%(balance)s)'),
                params={
                    'amount': amount,
                    'balance': balance['total_balance']
                }
            )
        
        return amount

    def save(self, commit=True):
        transaction = super().save(commit=False)
        transaction.loan = self.loan
        transaction.transaction_type = Transaction.Type.REPAYMENT
        
        if self.cleaned_data.get('reference'):
            if not transaction.payment_details:
                transaction.payment_details = {}
            transaction.payment_details['external_reference'] = self.cleaned_data['reference']
        
        if commit:
            # Process the payment using the repayment service
            repayment_service = RepaymentService(self.loan)
            transactions = repayment_service.process_payment(
                amount=self.cleaned_data['amount'],
                payment_method=self.cleaned_data['payment_method'],
                payment_details=transaction.payment_details,
                notes=self.cleaned_data.get('notes'),
                user=self.user
            )
            
            # Return the main repayment transaction
            return next(
                (t for t in transactions if t.transaction_type == Transaction.Type.REPAYMENT),
                transactions[0] if transactions else None
            )
        
        return transaction


class WaivePenaltyForm(forms.Form):
    """Form for waiving penalties on a repayment schedule."""
    
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.01'),
        widget=forms.NumberInput(attrs={'step': '0.01'})
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=True,
        help_text=_('Reason for waiving the penalty')
    )

    def __init__(self, *args, **kwargs):
        self.schedule = kwargs.pop('schedule')
        self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        
        # Calculate current penalty
        repayment_service = RepaymentService(self.schedule.loan)
        current_penalty = repayment_service.calculate_penalty(self.schedule)
        
        # Update amount field
        self.fields['amount'].widget.attrs.update({
            'max': current_penalty,
            'data-current-penalty': current_penalty
        })
        
        self.current_penalty = current_penalty

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount <= 0:
            raise ValidationError(_('Waiver amount must be greater than zero'))
            
        if amount > self.current_penalty:
            raise ValidationError(
                _('Waiver amount (%(amount)s) cannot exceed current penalty (%(penalty)s)'),
                params={
                    'amount': amount,
                    'penalty': self.current_penalty
                }
            )
        
        return amount

    def save(self):
        repayment_service = RepaymentService(self.schedule.loan)
        return repayment_service.waive_penalty(
            schedule=self.schedule,
            amount=self.cleaned_data['amount'],
            notes=self.cleaned_data['notes'],
            user=self.user
        )
