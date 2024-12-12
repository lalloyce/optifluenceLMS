from django.db import models
from decimal import Decimal
from django.conf import settings
from django.utils import timezone

class Payment(models.Model):
    loan = models.ForeignKey(
        'loans.Loan',
        on_delete=models.CASCADE,
        related_name='payments'
    )
    payment_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    reference_number = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Payment {self.reference_number} for Loan {self.loan.application_number}"
