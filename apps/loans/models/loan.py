from decimal import Decimal
from dateutil.relativedelta import relativedelta
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.customers.models import Customer
from django.conf import settings
from django.utils import timezone
from .loan_product import LoanProduct
from .loan_application import LoanApplication
from .repayment import RepaymentSchedule
from .config import LoanConfig
from django.shortcuts import get_object_or_404, redirect



class Loan(models.Model):
    """Model for individual loans."""
    
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', _('Draft')
        PENDING = 'PENDING', _('Pending Approval')
        APPROVED = 'APPROVED', _('Approved')
        REJECTED = 'REJECTED', _('Rejected')
        DISBURSED = 'DISBURSED', _('Disbursed')
        CLOSED = 'CLOSED', _('Closed')
        DEFAULTED = 'DEFAULTED', _('Defaulted')
    
    class RiskLevel(models.TextChoices):
        LOW = 'LOW', _('Low Risk')
        MODERATE = 'MODERATE', _('Moderate Risk')
        MEDIUM = 'MEDIUM', _('Medium Risk')
        HIGH = 'HIGH', _('High Risk')
    
    loan_product = models.ForeignKey(
        LoanProduct,
        on_delete=models.PROTECT,
        related_name='loans'
    )
    customer = models.ForeignKey(
        Customer,
        on_delete=models.PROTECT,
        related_name='loans'
    )
    loan_officer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='handled_loans'
    )
    application = models.OneToOneField(
        LoanApplication,
        on_delete=models.PROTECT,
        related_name='loan',
        null=True,
        blank=True
    )
    
    # Loan Details
    application_number = models.CharField(max_length=50, unique=True)
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    term_months = models.IntegerField(validators=[MinValueValidator(1)])
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    processing_fee = models.DecimalField(max_digits=10, decimal_places=2)
    repayment_schedule = models.ManyToManyField(RepaymentSchedule, related_name='loans_repayment_schedules', blank=True)

    def get_outstanding_amount(self):
        """Calculate and return the outstanding loan amount."""
        total_paid = sum(payment.amount for payment in self.payments.filter(status='PAID'))
        outstanding_amount = self.amount - total_paid
        return outstanding_amount

    def make_payment(self, request): 
        """Handle making a payment for this loan.""" 
        amount = Decimal(request.POST['amount']) # Example: get payment amount from POST data 
        payment_method = request.POST['payment_method'] 
        reference_number = request.POST['reference_number'] 
        payment = Payment.objects.create( 
            loan=self, payment_date=timezone.now(), 
            amount=amount, payment_method=payment_method, 
            reference_number=reference_number, status='PAID' ) 
        self.apply_payment(payment) 
        return redirect('customer_detail', pk=self.customer.pk)

    def apply_payment(self, payment):
        """Apply a payment to the loan and update the repayment schedule."""
        remaining_amount = payment.amount

        # Apply payment to each installment in order of due date
        for installment in self.repayment_schedule.filter(status__in=[RepaymentSchedule.Status.PENDING, RepaymentSchedule.Status.PARTIALLY_PAID]).order_by('due_date'):
            if remaining_amount <= 0:
                break

            due_amount = installment.remaining_amount()
            if remaining_amount >= due_amount:
                installment.paid_amount += due_amount
                installment.status = RepaymentSchedule.Status.PAID
                remaining_amount -= due_amount
            else:
                installment.paid_amount += remaining_amount
                installment.status = RepaymentSchedule.Status.PARTIALLY_PAID
                remaining_amount = 0

            installment.paid_date = timezone.now()
            installment.save()

        # Update loan status if fully paid
        if all(inst.status == RepaymentSchedule.Status.PAID for inst in self.repayment_schedule.all()):
            self.status = Loan.Status.CLOSED
            self.save()
    
    # Risk Assessment
    risk_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_('Calculated risk score (0-100)')
    )
    risk_level = models.CharField(
        max_length=20,
        choices=RiskLevel.choices,
        null=True,
        blank=True
    )
    risk_factors = models.JSONField(
        null=True,
        blank=True,
        help_text=_('Detailed risk assessment factors')
    )
    risk_notes = models.TextField(
        null=True,
        blank=True,
        help_text=_('Additional notes about risk assessment')
    )
    
    # Dates
    application_date = models.DateTimeField(auto_now_add=True)
    approval_date = models.DateTimeField(null=True, blank=True)
    disbursement_date = models.DateTimeField(null=True, blank=True)
    maturity_date = models.DateTimeField(null=True, blank=True)
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )
    
    # Additional Information
    purpose = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta: 
        verbose_name = _('loan') 
        verbose_name_plural = _('loans') 
        ordering = ['-application_date'] 
        
    def __str__(self): 
        return f"Loan {self.application_number} - {self.customer.full_name}" 
    
    def get_outstanding_amount(self): 
        """Calculate and return the outstanding loan amount.""" 
        total_paid = sum(payment.amount for payment in self.payments.filter(status='PAID')) 
        outstanding_amount = self.amount - total_paid 
        return outstanding_amount
    
    def save(self, *args, **kwargs):
        if not self.application_number:
            self.application_number = f"LN{timezone.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)
        
    def generate_repayment_schedule(self):
        """Generate repayment schedule for the loan."""
        if not self.disbursement_date:
            raise ValueError("Cannot generate schedule without disbursement date")
            
        # Delete existing schedule if any
        RepaymentSchedule.objects.filter(loan=self).delete()
        
        # Calculate amounts
        principal_per_installment = self.amount / self.term_months
        
        # Calculate total interest using simple interest
        annual_rate = self.interest_rate / Decimal('100')
        term_years = self.term_months / Decimal('12')
        total_interest = self.amount * annual_rate * term_years
        interest_per_installment = total_interest / self.term_months
        
        # Generate schedule
        for i in range(self.term_months):
            due_date = (self.disbursement_date + relativedelta(months=i + 1)).date()
            
            RepaymentSchedule.objects.create(
                loan=self,
                installment_number=i + 1,
                due_date=due_date,
                principal_amount=principal_per_installment,
                interest_amount=interest_per_installment,
                total_amount=principal_per_installment + interest_per_installment,
                penalty_amount=Decimal('0.00'),
                status=RepaymentSchedule.Status.PENDING
            )
    
    def update_risk_level(self):
        """Update risk level based on risk score."""
        if self.risk_score is None:
            return
            
        if self.risk_score >= 80:
            self.risk_level = self.RiskLevel.LOW
        elif self.risk_score >= 60:
            self.risk_level = self.RiskLevel.MODERATE
        elif self.risk_score >= 40:
            self.risk_level = self.RiskLevel.MEDIUM
        else:
            self.risk_level = self.RiskLevel.HIGH
        self.save()
    
    @classmethod
    def create_from_application(cls, application, loan_officer):
        """Create a new loan from an approved application."""
        if application.status != LoanApplication.Status.APPROVED:
            raise ValueError("Can only create loan from approved application")
            
        # Set disbursement date to today if not specified
        if not application.disbursement_date:
            application.disbursement_date = timezone.now()
            application.save()
            
        loan = cls.objects.create(
            loan_product=application.loan_product,
            customer=application.customer,
            loan_officer=loan_officer,
            application=application,
            application_number=application.application_number,
            amount=application.amount_requested,
            term_months=application.term_months,
            interest_rate=application.loan_product.interest_rate,
            processing_fee=application.loan_product.processing_fee,
            risk_score=getattr(application, 'risk_score', None),
            risk_level=getattr(application, 'risk_level', None),
            risk_factors=getattr(application, 'risk_factors', None),
            risk_notes=getattr(application, 'risk_notes', None),
            purpose=application.purpose,
            disbursement_date=application.disbursement_date,
            status=cls.Status.APPROVED
        )
        
        # Generate initial repayment schedule
        loan.generate_repayment_schedule()
        
        return loan
