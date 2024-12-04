# MPesa STK Push Integration

This module provides integration with Safaricom's MPesa STK Push service for payment processing.

## Setup

1. Add the required environment variables to your `.env` file:
```
MPESA_ENVIRONMENT=sandbox
MPESA_CONSUMER_KEY=your-consumer-key
MPESA_CONSUMER_SECRET=your-consumer-secret
MPESA_SHORTCODE=your-shortcode
MPESA_PASSKEY=your-passkey
MPESA_CALLBACK_URL=https://yourdomain.com/mpesa/api/callback/
```

2. Add 'apps.mpesastk' to INSTALLED_APPS in settings.py:
```python
INSTALLED_APPS = [
    ...
    'apps.mpesastk',
]
```

3. Include the URLs in your project's urls.py:
```python
urlpatterns = [
    ...
    path('mpesa/', include('apps.mpesastk.urls')),
]
```

## Features

- Initiate STK Push payments
- Track payment status
- View transaction history
- Query transaction status
- Handle MPesa callbacks

## Usage

### Making a Payment

1. Navigate to the payment page:
```
/mpesa/pay/
```

2. Enter the required details:
   - Phone Number (format: 254XXXXXXXXX)
   - Amount
   - Reference (optional)
   - Description (optional)

3. Click "Pay with MPesa" and follow the prompts on your phone

### Viewing Transactions

Access the transactions list at:
```
/mpesa/
```

### API Endpoints

1. Initiate STK Push:
```
POST /mpesa/api/stk-push/
{
    "phone": "254XXXXXXXXX",
    "amount": 100,
    "reference": "Optional reference",
    "description": "Optional description"
}
```

2. Query Transaction Status:
```
POST /mpesa/api/query/
{
    "checkout_request_id": "ws_CO_123456789"
}
```

3. MPesa Callback URL:
```
POST /mpesa/api/callback/
```

## Models

### STKTransaction

Stores MPesa STK Push transaction details:

- merchant_request_id
- checkout_request_id
- result_code
- result_desc
- amount
- phone_number
- reference
- description
- status (pending/successful/failed)
- created_at
- updated_at

## Services

### MPesaSTKService

Handles all MPesa API interactions:

- initiate_stk_push(): Initiates an STK Push request
- query_stk_status(): Queries the status of a transaction
- process_callback(): Processes MPesa callbacks

## Security

1. All API endpoints are protected with CSRF tokens
2. Callback URL is secured with MPesa's IP whitelist
3. Sensitive credentials are stored in environment variables
4. All transactions are logged for audit purposes

## Error Handling

The module includes comprehensive error handling for:
- Network errors
- Invalid phone numbers
- Insufficient funds
- Cancelled transactions
- Timeout errors

## Logging

All MPesa interactions are logged using Django's logging system:
- API requests and responses
- Transaction status updates
- Error messages

## Testing

Run the tests using:
```bash
python manage.py test apps.mpesastk
```

## Troubleshooting

1. Invalid Phone Number:
   - Ensure phone number is in format: 254XXXXXXXXX
   - Number must be registered with MPesa

2. Transaction Failed:
   - Check user has sufficient funds
   - Verify MPesa service is available
   - Confirm API credentials are correct

3. Callback Not Received:
   - Verify callback URL is accessible
   - Check MPesa IP whitelist
   - Review server logs for errors

## Support

For support:
1. Check the logs in your Django application
2. Review MPesa documentation
3. Contact Safaricom developer support
4. Open an issue in the project repository
