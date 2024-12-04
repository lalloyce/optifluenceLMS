"""MPesa STK Push utility functions."""
import re
from decimal import Decimal
from .exceptions import InvalidPhoneNumberError, InvalidAmountError

def validate_phone_number(phone_number: str) -> str:
    """
    Validate and format phone number.
    
    Args:
        phone_number (str): Phone number to validate
        
    Returns:
        str: Formatted phone number
        
    Raises:
        InvalidPhoneNumberError: If phone number is invalid
    """
    # Remove any spaces or special characters
    phone = re.sub(r'[^0-9]', '', phone_number)
    
    # Check if it's a valid Kenyan phone number
    if not re.match(r'^254[17]\d{8}$', phone):
        if re.match(r'^0[17]\d{8}$', phone):
            # Convert from 07... to 2547...
            phone = '254' + phone[1:]
        else:
            raise InvalidPhoneNumberError(
                'Invalid phone number format. Use format: 254XXXXXXXXX'
            )
    
    return phone

def validate_amount(amount: str | int | float | Decimal) -> int:
    """
    Validate and format amount.
    
    Args:
        amount: Amount to validate
        
    Returns:
        int: Amount in cents/cents
        
    Raises:
        InvalidAmountError: If amount is invalid
    """
    try:
        # Convert to Decimal for precise handling
        decimal_amount = Decimal(str(amount))
        
        # Check if amount is positive
        if decimal_amount <= 0:
            raise InvalidAmountError('Amount must be greater than 0')
        
        # Check if amount has more than 2 decimal places
        if decimal_amount.as_tuple().exponent < -2:
            raise InvalidAmountError('Amount cannot have more than 2 decimal places')
        
        # Convert to cents/cents (multiply by 100 and round)
        return int(decimal_amount * 100)
        
    except (ValueError, TypeError, InvalidAmountError) as e:
        raise InvalidAmountError(f'Invalid amount: {str(e)}')

def format_phone_display(phone_number: str) -> str:
    """
    Format phone number for display.
    
    Args:
        phone_number (str): Phone number to format
        
    Returns:
        str: Formatted phone number (e.g., 0712 345 678)
    """
    if phone_number.startswith('254'):
        phone = '0' + phone_number[3:]
    else:
        phone = phone_number
    
    # Format as: 0712 345 678
    return f'{phone[:4]} {phone[4:7]} {phone[7:]}'

def mask_phone_number(phone_number: str) -> str:
    """
    Mask phone number for privacy.
    
    Args:
        phone_number (str): Phone number to mask
        
    Returns:
        str: Masked phone number (e.g., 254712***678)
    """
    if len(phone_number) < 8:
        return phone_number
    
    return f'{phone_number[:-6]}***{phone_number[-3:]}'

def generate_transaction_reference() -> str:
    """
    Generate a unique transaction reference.
    
    Returns:
        str: Unique transaction reference
    """
    import uuid
    import time
    
    # Generate timestamp-based prefix
    prefix = time.strftime('%Y%m%d%H%M%S')
    
    # Generate random suffix
    suffix = str(uuid.uuid4().hex)[:6]
    
    return f'TXN{prefix}{suffix}'

def format_amount_display(amount_cents: int) -> str:
    """
    Format amount for display.
    
    Args:
        amount_cents (int): Amount in cents/cents
        
    Returns:
        str: Formatted amount (e.g., KES 1,234.56)
    """
    amount = Decimal(amount_cents) / Decimal(100)
    return f'KES {amount:,.2f}'

def is_business_hours() -> bool:
    """
    Check if current time is within business hours (6 AM to 12 AM EAT).
    
    Returns:
        bool: True if within business hours
    """
    from datetime import datetime
    import pytz
    
    # Get current time in EAT
    tz = pytz.timezone('Africa/Nairobi')
    now = datetime.now(tz)
    
    # Check if time is between 6 AM and 12 AM
    return 6 <= now.hour < 24

def calculate_transaction_charge(amount: int) -> int:
    """
    Calculate MPesa transaction charge.
    
    Args:
        amount (int): Transaction amount in cents
        
    Returns:
        int: Transaction charge in cents
    """
    # MPesa transaction charges (as of 2023)
    charge_tiers = [
        (100, 0),         # 1-100: Free
        (1000, 11),       # 101-1000: 11
        (2500, 28),       # 1001-2500: 28
        (5000, 50),       # 2501-5000: 50
        (10000, 84),      # 5001-10000: 84
        (15000, 112),     # 10001-15000: 112
        (20000, 140),     # 15001-20000: 140
        (35000, 196),     # 20001-35000: 196
        (50000, 224),     # 35001-50000: 224
        (150000, 280),    # 50001-150000: 280
    ]
    
    amount_ksh = amount / 100  # Convert cents to KES
    
    for tier_amount, charge in charge_tiers:
        if amount_ksh <= tier_amount:
            return charge * 100  # Convert charge to cents
    
    return 280 * 100  # Maximum charge for amounts over 150,000
