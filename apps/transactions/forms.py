from django import forms
from django.utils import timezone
from .models import Transaction
from apps.customers.models import Customer
from apps.loans.models import Loan

class TransactionForm(forms.ModelForm):
    """Form for creating and editing transactions."""
    
    class Meta:
        model = Transaction
        fields = [
            'customer',
            'loan',
            'amount',
            'transaction_type',
            'transaction_date',
            'reference_number',
            'notes'
        ]
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control select2', 'data-placeholder': 'Select Customer'}),
            'loan': forms.Select(attrs={'class': 'form-control select2', 'data-placeholder': 'Select Loan'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter amount'}),
            'transaction_type': forms.Select(attrs={'class': 'form-control select2', 'data-placeholder': 'Select Transaction Type'}),
            'transaction_date': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter reference number (optional)'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter any additional notes (optional)'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial transaction date to now
        self.fields['transaction_date'].initial = timezone.now()
        
        # Initialize customer queryset
        self.fields['customer'].queryset = Customer.objects.filter(is_active=True)
        
        # Make loan field dependent on customer selection
        if not self.is_bound:  # If form is not submitted
            self.fields['loan'].queryset = Loan.objects.none()
        
        if 'customer' in self.data:
            try:
                customer_id = int(self.data.get('customer'))
                self.fields['loan'].queryset = Loan.objects.filter(
                    customer_id=customer_id,
                    status='DISBURSED'
                ).select_related('customer')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.customer:
            # If editing an existing transaction, show loans for the selected customer
            self.fields['loan'].queryset = Loan.objects.filter(
                customer=self.instance.customer,
                status='DISBURSED'
            ).select_related('customer')
    
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
