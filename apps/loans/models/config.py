from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.conf import settings

class LoanConfig(models.Model):
    """Configuration model for loan parameters."""
    
    class LoanType(models.TextChoices):
        PERSONAL = 'PERSONAL', 'Personal Loan'
        BUSINESS = 'BUSINESS', 'Business Loan'
    
    loan_type = models.CharField(
        max_length=20,
        choices=LoanType.choices,
        help_text="Type of loan this configuration applies to"
    )
    
    # Interest Configuration
    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Annual interest rate as a percentage (e.g., 10.00 for 10%)"
    )
    
    # Term Configuration
    term_days = models.PositiveIntegerField(
        help_text="Loan term in days"
    )
    
    # Penalty Configuration
    penalty_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Monthly penalty rate as a percentage (e.g., 10.00 for 10%)"
    )
    
    # Validity Period
    effective_from = models.DateTimeField(
        default=timezone.now,
        help_text="When these parameters become effective"
    )
    effective_to = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When these parameters expire (null for current configuration)"
    )
    
    # Audit Fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='loan_configs_created'
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='loan_configs_updated'
    )
    
    class Meta:
        ordering = ['-effective_from']
        constraints = [
            models.CheckConstraint(
                check=models.Q(effective_to__isnull=True) | models.Q(effective_to__gt=models.F('effective_from')),
                name='effective_to_after_from'
            )
        ]
    
    def __str__(self):
        return f"{self.get_loan_type_display()} Config (Effective: {self.effective_from.date()})"
    
    @classmethod
    def get_current_config(cls, loan_type):
        """Get the current configuration for a loan type."""
        now = timezone.now()
        return cls.objects.filter(
            loan_type=loan_type,
            effective_from__lte=now
        ).filter(
            models.Q(effective_to__isnull=True) |
            models.Q(effective_to__gt=now)
        ).first()
    
    def save(self, *args, **kwargs):
        if not self.pk and not self.effective_to:
            # When creating a new current config, expire the previous one
            current_config = LoanConfig.get_current_config(self.loan_type)
            if current_config:
                current_config.effective_to = self.effective_from
                current_config.save()
        super().save(*args, **kwargs)
