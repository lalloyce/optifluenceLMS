"""Transaction management services."""
from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from .models import Transaction, RepaymentSchedule
from apps.accounts.models import AuditLog
from apps.accounts.audit import log_event

class TransactionService:
    """Service class for transaction management."""
    
    @staticmethod
    def create_transaction(loan, amount, transaction_type, user, description=None):
        """Create a new transaction."""
        with transaction.atomic():
            trans = Transaction.objects.create(
                loan=loan,
                amount=amount,
                transaction_type=transaction_type,
                processed_by=user,
                description=description,
                status=Transaction.Status.COMPLETED
            )
            
            if transaction_type == Transaction.Type.REPAYMENT:
                TransactionService._process_repayment(trans)
            
            log_event(
                None,
                AuditLog.EventType.TRANSACTION_CREATE,
                f"Transaction {trans.reference_number} created",
                user=user,
                status='SUCCESS'
            )
            
            return trans
    
    @staticmethod
    def reverse_transaction(transaction, user):
        """Reverse an existing transaction."""
        with transaction.atomic():
            # Create reversal transaction
            reversal = Transaction.objects.create(
                loan=transaction.loan,
                transaction_type=transaction.transaction_type,
                amount=-transaction.amount,
                status=Transaction.Status.COMPLETED,
                processed_by=user,
                description=f'Reversal of transaction {transaction.reference_number}',
                reference_number=f'REV-{transaction.reference_number}'
            )
            
            # Update original transaction status
            transaction.status = Transaction.Status.REVERSED
            transaction.save()
            
            if transaction.transaction_type == Transaction.Type.REPAYMENT:
                TransactionService._reverse_repayment(transaction)
            
            log_event(
                None,
                AuditLog.EventType.TRANSACTION_REVERSE,
                f"Transaction {transaction.reference_number} reversed",
                user=user,
                status='SUCCESS'
            )
            
            return reversal
    
    @staticmethod
    def _process_repayment(transaction):
        """Process a repayment transaction."""
        loan = transaction.loan
        amount_remaining = transaction.amount
        
        # Find pending schedules and apply payment
        pending_schedules = loan.repayment_schedule.filter(
            status=RepaymentSchedule.Status.PENDING
        ).order_by('due_date')
        
        for schedule in pending_schedules:
            if amount_remaining <= 0:
                break
                
            amount_to_pay = min(amount_remaining, schedule.amount_due - schedule.amount_paid)
            schedule.amount_paid += amount_to_pay
            amount_remaining -= amount_to_pay
            
            if schedule.amount_paid >= schedule.amount_due:
                schedule.status = RepaymentSchedule.Status.PAID
                schedule.paid_date = timezone.now()
            
            schedule.save()
    
    @staticmethod
    def _reverse_repayment(transaction):
        """Reverse a repayment transaction."""
        loan = transaction.loan
        amount_to_reverse = transaction.amount
        
        # Find paid schedules and reverse payment
        paid_schedules = loan.repayment_schedule.filter(
            status=RepaymentSchedule.Status.PAID,
            paid_date__lte=transaction.transaction_date
        ).order_by('-paid_date')
        
        for schedule in paid_schedules:
            if amount_to_reverse <= 0:
                break
                
            amount_reversed = min(amount_to_reverse, schedule.amount_paid)
            schedule.amount_paid -= amount_reversed
            amount_to_reverse -= amount_reversed
            
            if schedule.amount_paid < schedule.amount_due:
                schedule.status = RepaymentSchedule.Status.PENDING
                schedule.paid_date = None
            
            schedule.save()
