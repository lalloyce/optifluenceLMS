"""MPesa STK Push custom exceptions."""

class MPesaError(Exception):
    """Base exception for MPesa-related errors."""
    pass

class MPesaConnectionError(MPesaError):
    """Raised when there's an error connecting to MPesa API."""
    pass

class MPesaAuthenticationError(MPesaError):
    """Raised when there's an error with MPesa authentication."""
    pass

class MPesaValidationError(MPesaError):
    """Raised when there's a validation error with MPesa request."""
    pass

class MPesaTransactionError(MPesaError):
    """Raised when there's an error processing MPesa transaction."""
    pass

class MPesaCallbackError(MPesaError):
    """Raised when there's an error processing MPesa callback."""
    pass

class InvalidPhoneNumberError(MPesaValidationError):
    """Raised when phone number format is invalid."""
    pass

class InvalidAmountError(MPesaValidationError):
    """Raised when amount is invalid."""
    pass

class TransactionNotFoundError(MPesaError):
    """Raised when transaction is not found."""
    pass

class DuplicateTransactionError(MPesaError):
    """Raised when attempting to process duplicate transaction."""
    pass
