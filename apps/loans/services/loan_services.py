from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from apps.loans.models import RepaymentSchedule  # Keep this import outside the function

def apply_payment(loan, payment):
    """Apply a payment to the loan and update the repayment schedule."""
    from apps.loans.models import Payment  # Import Payment within the function
    remaining_amount = payment.amount

    # Apply payment to each installment in order of due date
    for installment in loan.repayment_schedule.filter(status__in=[RepaymentSchedule.Status.PENDING, RepaymentSchedule.Status.PARTIALLY_PAID]).order_by('due_date'):
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
    if all(inst.status == RepaymentSchedule.Status.PAID for inst in loan.repayment_schedule.all()):
        loan.status = Loan.Status.CLOSED
        loan.save()

def record_payment(loan, installment_id, amount, payment_date, notes):
    """Business logic for recording a payment for a loan installment."""
    try:
        installment = loan.repayment_schedule.get(id=installment_id)
        remaining = installment.total_amount - installment.paid_amount
        
        if amount > remaining:
            return f'Payment amount cannot exceed remaining amount of KES {remaining}', False
        else:
            installment.paid_amount += amount
            installment.payment_date = payment_date
            if notes:
                installment.notes = (installment.notes or '') + f'\n{timezone.now()}: {notes}'
            installment.save()
            installment.update_status()
            
            return f'Payment of KES {amount} recorded successfully', True
    except RepaymentSchedule.DoesNotExist:
        return 'Invalid installment selected', False
    except ValueError:
        return 'Invalid payment amount', False
