from django import template
from decimal import Decimal

register = template.Library()

@register.filter
def sub(value, arg):
    """Subtract the arg from the value."""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return value

@register.filter
def currency(value):
    """Format value as currency."""
    try:
        return "{:,.2f}".format(float(value))
    except (ValueError, TypeError):
        return value

@register.filter
def percentage(value):
    """Format value as percentage."""
    try:
        return "{:.1f}%".format(float(value) * 100)
    except (ValueError, TypeError):
        return value

@register.filter
def remaining_balance(loan):
    """Calculate remaining balance for a loan."""
    try:
        total_paid = sum(i.paid_amount for i in loan.repayment_schedule.all())
        return loan.loan_amount - Decimal(str(total_paid))
    except (ValueError, TypeError, AttributeError):
        return 0
