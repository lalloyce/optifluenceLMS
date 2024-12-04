from django import forms
from .models import Transaction
from apps.loans.models import Loan

class TransactionForm(forms.ModelForm):
    """Form for creating and editing transactions."""
    
    class Meta:
        model = Transaction
        fields = [
            'loan',
            'transaction_type',
            'amount',
            'reference_number',
            'description',
            'status'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active loans in the dropdown
        self.fields['loan'].queryset = Loan.objects.filter(
            status__in=[Loan.Status.DISBURSED, Loan.Status.DEFAULTED]
        )
    
    def clean_amount(self):
        """Validate transaction amount."""
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise forms.ValidationError('Amount must be greater than zero.')
        return amount
    
    def clean_reference_number(self):
        """Validate reference number is unique."""
        ref_num = self.cleaned_data.get('reference_number')
        if ref_num:
            if Transaction.objects.filter(reference_number=ref_num).exclude(
                pk=self.instance.pk if self.instance else None
            ).exists():
                raise forms.ValidationError('This reference number has already been used.')
        return ref_num
    
    def clean(self):
        """Additional validation for the entire form."""
        cleaned_data = super().clean()
        loan = cleaned_data.get('loan')
        amount = cleaned_data.get('amount')
        transaction_type = cleaned_data.get('transaction_type')
        
        if loan and amount and transaction_type:
            if transaction_type == Transaction.TransactionType.REPAYMENT:
                # Get the next pending repayment amount
                next_repayment = loan.repayment_schedule.filter(status='PENDING').first()
                if next_repayment and amount > next_repayment.total_amount:
                    raise forms.ValidationError(
                        f'Repayment amount ({amount}) cannot exceed the scheduled amount ({next_repayment.total_amount})'
                    )
            elif transaction_type == Transaction.TransactionType.DISBURSEMENT:
                if amount != loan.amount_approved:
                    raise forms.ValidationError(
                        f'Disbursement amount must equal the approved loan amount ({loan.amount_approved})'
                    )
        
        return cleaned_data
