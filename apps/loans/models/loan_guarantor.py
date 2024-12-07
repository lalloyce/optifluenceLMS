from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.customers.models import Customer

class LoanGuarantor(models.Model):
    """Model for loan guarantors."""
    
    loan = models.ForeignKey(
        'Loan',
        on_delete=models.CASCADE,
        related_name='guarantors'
    )
    guarantor = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='guaranteed_loans'
    )
    guarantee_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text=_('Amount guaranteed by this guarantor')
    )
    guarantee_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100)
        ],
        help_text=_('Percentage of loan amount guaranteed')
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', _('Pending')),
            ('APPROVED', _('Approved')),
            ('REJECTED', _('Rejected')),
            ('WITHDRAWN', _('Withdrawn'))
        ],
        default='PENDING'
    )
    
    # Documents and verification (optional)
    id_document = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text=_('Path to guarantor\'s ID document (optional)')
    )
    income_proof = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text=_('Path to guarantor\'s income proof (optional)')
    )
    verified = models.BooleanField(
        default=False,
        help_text=_('Whether the guarantor has been verified')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('loan guarantor')
        verbose_name_plural = _('loan guarantors')
        unique_together = ['loan', 'guarantor']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.guarantor.get_full_name()} - {self.loan.application_number}"
