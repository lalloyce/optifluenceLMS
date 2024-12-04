"""MPesa STK Push services."""
import json
import base64
import requests
from datetime import datetime
from django.conf import settings
from django.utils import timezone
import logging
from .models import STKTransaction

logger = logging.getLogger(__name__)

class MPesaSTKService:
    """Service for handling MPesa STK Push operations."""
    
    def __init__(self):
        """Initialize MPesa configuration."""
        self.business_shortcode = settings.MPESA_SHORTCODE
        self.passkey = settings.MPESA_PASSKEY
        self.consumer_key = settings.MPESA_CONSUMER_KEY
        self.consumer_secret = settings.MPESA_CONSUMER_SECRET
        self.access_token_url = f"{settings.MPESA_API_URL}/oauth/v1/generate?grant_type=client_credentials"
        self.process_request_url = f"{settings.MPESA_API_URL}/mpesa/stkpush/v1/processrequest"
        self.query_request_url = f"{settings.MPESA_API_URL}/mpesa/stkpushquery/v1/query"
        self.callback_url = settings.MPESA_CALLBACK_URL
    
    def _get_password(self):
        """Generate the MPesa password."""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password_str = f"{self.business_shortcode}{self.passkey}{timestamp}"
        return base64.b64encode(password_str.encode()).decode('utf-8'), timestamp
    
    def _get_access_token(self):
        """Get MPesa access token."""
        try:
            credentials = base64.b64encode(
                f"{self.consumer_key}:{self.consumer_secret}".encode()
            ).decode('utf-8')
            
            headers = {
                'Authorization': f"Basic {credentials}"
            }
            
            response = requests.get(self.access_token_url, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            return result.get('access_token')
            
        except Exception as e:
            logger.error(f"Error getting MPesa access token: {str(e)}")
            raise
    
    def initiate_stk_push(self, phone_number, amount, reference, description):
        """Initiate STK Push request."""
        try:
            access_token = self._get_access_token()
            password, timestamp = self._get_password()
            
            headers = {
                'Authorization': f"Bearer {access_token}",
                'Content-Type': 'application/json'
            }
            
            payload = {
                "BusinessShortCode": self.business_shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": int(amount),
                "PartyA": phone_number,
                "PartyB": self.business_shortcode,
                "PhoneNumber": phone_number,
                "CallBackURL": self.callback_url,
                "AccountReference": reference,
                "TransactionDesc": description
            }
            
            response = requests.post(
                self.process_request_url,
                headers=headers,
                data=json.dumps(payload)
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Create transaction record
            transaction = STKTransaction.objects.create(
                merchant_request_id=result['MerchantRequestID'],
                checkout_request_id=result['CheckoutRequestID'],
                amount=amount,
                phone_number=phone_number,
                reference=reference,
                description=description
            )
            
            logger.info(
                f"STK Push initiated: {transaction.checkout_request_id} "
                f"for {phone_number} amount {amount}"
            )
            
            return transaction
            
        except Exception as e:
            logger.error(f"Error initiating STK Push: {str(e)}")
            raise
    
    def query_stk_status(self, checkout_request_id):
        """Query the status of an STK Push request."""
        try:
            access_token = self._get_access_token()
            password, timestamp = self._get_password()
            
            headers = {
                'Authorization': f"Bearer {access_token}",
                'Content-Type': 'application/json'
            }
            
            payload = {
                "BusinessShortCode": self.business_shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "CheckoutRequestID": checkout_request_id
            }
            
            response = requests.post(
                self.query_request_url,
                headers=headers,
                data=json.dumps(payload)
            )
            response.raise_for_status()
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Error querying STK status: {str(e)}")
            raise
    
    def process_callback(self, callback_data):
        """Process STK Push callback."""
        try:
            body = callback_data.get('Body', {})
            result = body.get('stkCallback', {})
            
            merchant_request_id = result.get('MerchantRequestID')
            checkout_request_id = result.get('CheckoutRequestID')
            result_code = result.get('ResultCode')
            result_desc = result.get('ResultDesc')
            
            # Update transaction
            transaction = STKTransaction.objects.get(
                checkout_request_id=checkout_request_id
            )
            
            transaction.result_code = result_code
            transaction.result_desc = result_desc
            transaction.status = 'successful' if result_code == '0' else 'failed'
            transaction.save()
            
            logger.info(
                f"STK Push callback processed: {checkout_request_id} "
                f"status: {transaction.status}"
            )
            
            return transaction
            
        except STKTransaction.DoesNotExist:
            logger.error(f"Transaction not found for checkout_request_id: {checkout_request_id}")
            raise
        except Exception as e:
            logger.error(f"Error processing STK callback: {str(e)}")
            raise
