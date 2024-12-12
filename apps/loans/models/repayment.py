from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.utils import timezone


class RepaymentSchedule(models.Model):
    """Model for loan repayment schedules."""
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        PARTIALLY_PAID = 'PARTIALLY_PAID', _('Partially Paid')
        PAID = 'PAID', _('Paid')
        OVERDUE = 'OVERDUE', _('Overdue')
    
    loan = models.ForeignKey('Loan', on_delete=models.CASCADE, related_name='loan_repayment_schedules')

    installment_number = models.IntegerField()
    due_date = models.DateField()
    principal_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    interest_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    penalty_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    paid_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    paid_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['due_date', 'installment_number']
        unique_together = ['loan', 'installment_number']
    
    def __str__(self):
        return f"Repayment {self.installment_number} for Loan {self.loan.application_number}"
    
    def remaining_amount(self):
        """Calculate remaining amount to be paid."""
        return self.total_amount - self.paid_amount
    
    def is_overdue(self):
        """Check if payment is overdue."""
        return self.status != self.Status.PAID and self.due_date < timezone.now().date()
    
    def update_status(self):
        """Update payment status based on amounts and due date."""
        if self.paid_amount >= self.total_amount:
            self.status = self.Status.PAID
        elif self.paid_amount > 0:
            self.status = self.Status.PARTIALLY_PAID
        elif self.is_overdue():
            self.status = self.Status.OVERDUE
        else:
            self.status = self.Status.PENDING
        self.save()
