from decimal import Decimal 
from django.utils import timezone 
from django.db import transaction 
from django.db.models import Sum, F 
from apps.loans.models.config import LoanConfig

class RepaymentService: 
    """Service for handling loan repayments and calculations.""" 
    
    def __init__(self, loan): 
        self.loan = loan 
        self.config = LoanConfig.get_current_config(loan.loan_type) 
        if not self.config: 
            raise ValueError(f"No configuration found for loan type: {loan.loan_type}") 
    
    def calculate_penalty(self, schedule): 
        """Calculate penalty for overdue payment.""" 
        from apps.loans.models import RepaymentSchedule
        if not schedule.is_overdue: 
            return Decimal('0.00') 
        
        days_overdue = (timezone.now().date() - schedule.due_date).days 
        if days_overdue <= 0: 
            return Decimal('0.00') 
        
        months_overdue = (days_overdue + 29) // 30 # Round up to nearest month 
        
        loan_balance = self.get_loan_balance() 
        total_outstanding = loan_balance['total_balance'] 
        
        annual_penalty_rate = self.loan.loan_product.penalty_rate / Decimal('100') 
        monthly_penalty_rate = annual_penalty_rate / Decimal('12') 
        penalty_amount = total_outstanding * monthly_penalty_rate * months_overdue 
        
        return min(penalty_amount, total_outstanding)
    
    def calculate_interest(self, principal):
        """Calculate simple interest for the loan."""
        interest_rate = Decimal('10') / Decimal('100')
        return (principal * interest_rate).quantize(Decimal('0.01'))
    
    def process_payment(self, amount, payment_method, payment_details=None, notes=None, user=None): 
        """Process a loan repayment.""" 
        from apps.loans.models import RepaymentSchedule, Transaction 
        if amount <= 0: 
            raise ValueError("Payment amount must be greater than zero") 
        
        pending_schedules = self.loan.repayment_schedule.exclude( 
            status=RepaymentSchedule.Status.PAID 
        ).order_by('due_date') 
        
        if not pending_schedules.exists(): 
            raise ValueError("No pending repayments found") 
            
        remaining_amount = amount 
        transactions = [] 
        
        with transaction.atomic(): 
            # Process penalties first 
            for schedule in pending_schedules: 
                if remaining_amount <= 0: 
                    break 
                
                penalty = self.calculate_penalty(schedule) 
                if penalty > 0: 
                    penalty_payment = min(penalty, remaining_amount) 
                    penalty_transaction = Transaction.objects.create( 
                        loan=self.loan, 
                        repayment_schedule=schedule, 
                        transaction_type=Transaction.Type.PENALTY, 
                        amount=penalty_payment, 
                        payment_method=payment_method, 
                        payment_details=payment_details,
                        notes=f"Penalty payment for installment {schedule.installment_number}" 
                    ) 
                    transactions.append(penalty_transaction) 
                    remaining_amount -= penalty_payment 
                        
            # Process regular repayments 
            for schedule in pending_schedules: 
                if remaining_amount <= 0: 
                    break 
                
                payment_amount = min(schedule.remaining_amount(), remaining_amount) 
                repayment_transaction = Transaction.objects.create( 
                    loan=self.loan, 
                    repayment_schedule=schedule, 
                    transaction_type=Transaction.Type.REPAYMENT, 
                    amount=payment_amount, 
                    payment_method=payment_method, 
                    payment_details=payment_details, 
                    notes=notes 
                ) 
                transactions.append(repayment_transaction) 
                remaining_amount -= payment_amount 
            
            for txn in transactions: 
                txn.complete_transaction(user) 
            
            self._update_loan_status() 
        
        return
    
    def waive_penalty(self, schedule, amount, notes=None, user=None):
        """Waive penalty amount for a schedule."""
        penalty = self.calculate_penalty(schedule)
        if amount > penalty:
            raise ValueError("Waiver amount cannot exceed penalty amount")
            
        waiver_transaction = Transaction.objects.create(
            loan=self.loan,
            repayment_schedule=schedule,
            transaction_type=Transaction.Type.WAIVER,
            amount=amount,
            notes=notes or f"Penalty waiver for installment {schedule.installment_number}"
        )
        waiver_transaction.complete_transaction(user)
        
        return waiver_transaction
    
    def generate_repayment_schedule(self):
        """Generate repayment schedule for a newly disbursed loan."""
        if self.loan.status != Loan.Status.DISBURSED:
            raise ValueError("Can only generate schedule for disbursed loans")
            
        if self.loan.repayment_schedule.exists():
            raise ValueError("Repayment schedule already exists")
        
        principal = self.loan.amount
        start_date = self.loan.disbursement_date
        end_date = start_date + timezone.timedelta(days=self.config.term_days)
        
        total_interest = self.calculate_interest(principal)
        
        schedule = RepaymentSchedule.objects.create(
            loan=self.loan,
            installment_number=1,
            due_date=end_date,
            principal_amount=principal,
            interest_amount=total_interest,
            total_amount=principal + total_interest
        )
        
        return [schedule]
    
    def get_loan_balance(self):
        """Get current loan balance including principal, interest and penalties."""
        if not self.loan.disbursement_date:
            raise ValueError("Loan has not been disbursed yet")
            
        total_paid = self.loan.transactions.filter(
            status=Transaction.Status.COMPLETED
        ).aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        total_loan_amount = self.loan.amount + self.calculate_total_interest()
        
        total_penalties = sum(
            self.calculate_penalty(schedule)
            for schedule in self.loan.repayment_schedule.all()
        )
        
        return {
            'total_balance': total_loan_amount + total_penalties - total_paid,
            'principal_balance': self.loan.amount,
            'interest_balance': self.calculate_total_interest(),
            'penalty_balance': total_penalties,
            'total_paid': total_paid
        }
    
    def calculate_total_interest(self):
        """Calculate total interest for the loan based on disbursement date."""
        if not self.loan.disbursement_date:
            return Decimal('0.00')
            
        principal = self.loan.amount
        annual_rate = self.loan.interest_rate / Decimal('100')
        term_years = self.loan.term_months / Decimal('12')
        
        total_interest = principal * annual_rate * term_years
        return total_interest.quantize(Decimal('0.01'))
    
    def _calculate_payment_progress(self):
        """Calculate overall payment progress as percentage."""
        total_due = self.loan.repayment_schedule.aggregate(
            total=Sum('total_amount')
        )['total'] or Decimal('0.00')
        
        if total_due == 0:
            return 100
            
        total_paid = self.loan.repayment_schedule.aggregate(
            paid=Sum('paid_amount')
        )['paid'] or Decimal('0.00')
        
        progress = (total_paid / total_due * 100).quantize(Decimal('0.01'))
        return min(progress, 100)
    
    def _update_loan_status(self):
        """Update loan status based on repayment completion."""
        pending_amount = self.loan.repayment_schedule.aggregate(
            pending=Sum(F('total_amount') - F('paid_amount'))
        )['pending'] or Decimal('0.00')
        
        if pending_amount <= 0:
            self.loan.status = Loan.Status.CLOSED
            self.loan.closed_date = timezone.now().date()
            self.loan.save()
    
    def _get_next_due_date(self, current_date):
        """Calculate next due date, considering month end dates."""
        year = current_date.year + ((current_date.month + 1) - 1) // 12
        month = ((current_date.month + 1) - 1) % 12 + 1
        day = min(current_date.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
                                   31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
        return current_date.replace(year=year, month=month, day=day)
