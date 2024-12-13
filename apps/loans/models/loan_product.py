from decimal import Decimal
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

class LoanProduct(models.Model):
    """Model for different types of loan products."""
    
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    minimum_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    maximum_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    minimum_term = models.IntegerField()
    maximum_term = models.IntegerField()
    processing_fee = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Loan terms and fees
    term_months = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text=_('Default term length in months'),
        default=1  # Default 1 month term
    )
    grace_period_months = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text=_('Grace period in months before first payment is due')
    )
    penalty_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_('Annual penalty rate for late payments'),
        default=Decimal('10.00')  # Default 10% annual penalty rate
    )
    insurance_fee = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_('Insurance fee as percentage of loan amount'),
        default=Decimal('0.00')  # Default 0% insurance fee
    )
    
    # Documentation and eligibility
    required_documents = models.JSONField(
        null=True,
        blank=True,
        help_text=_('List of required documents for loan application')
    )
    eligibility_criteria = models.JSONField(
        null=True,
        blank=True,
        help_text=_('Eligibility criteria for loan approval')
    )
    
    # Risk-based limits
    high_risk_max_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text=_('Maximum amount for high-risk loans (score < 40)')
    )
    medium_risk_max_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text=_('Maximum amount for medium-risk loans (score 40-59)')
    )
    moderate_risk_max_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text=_('Maximum amount for moderate-risk loans (score 60-79)')
    )
    
    # Risk thresholds for automatic approval/rejection
    auto_reject_below = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=30,
        help_text=_('Automatically reject loans with risk score below this value')
    )
    auto_approve_above = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=80,
        help_text=_('Automatically approve loans with risk score above this value')
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('loan product')
        verbose_name_plural = _('loan products')
    
    def __str__(self):
        return self.name
    
    def get_max_amount_for_risk_score(self, risk_score):
        """Get maximum allowed amount based on risk score."""
        if risk_score >= 80:
            return self.maximum_amount
        elif risk_score >= 60:
            return self.moderate_risk_max_amount
        elif risk_score >= 40:
            return self.medium_risk_max_amount
        else:
            return self.high_risk_max_amount
