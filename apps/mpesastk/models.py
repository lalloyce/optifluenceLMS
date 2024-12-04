from django.db import models
from django.utils import timezone


class STKTransaction(models.Model):
    merchant_request_id = models.CharField(max_length=50)
    checkout_request_id = models.CharField(max_length=50)
    result_code = models.CharField(max_length=5, null=True)
    result_desc = models.CharField(max_length=120, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    phone_number = models.CharField(max_length=15)
    reference = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('successful', 'Successful'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'STK Transaction'
        verbose_name_plural = 'STK Transactions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.phone_number} - {self.amount} - {self.status}"
