"""Tests for MPesa STK Push integration."""
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import STKTransaction
from .services import MPesaSTKService

User = get_user_model()

class MPesaSTKTests(TestCase):
    """Test MPesa STK Push functionality."""
    
    def setUp(self):
        """Set up test data."""
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.client.login(email='test@example.com', password='testpass123')
        
        # Sample transaction data
        self.transaction_data = {
            'phone': '254712345678',
            'amount': 100,
            'reference': 'TEST123',
            'description': 'Test payment'
        }
        
        # Sample MPesa response
        self.mpesa_response = {
            'MerchantRequestID': 'test-merchant-id',
            'CheckoutRequestID': 'test-checkout-id',
            'ResponseCode': '0',
            'ResponseDescription': 'Success',
            'CustomerMessage': 'Success'
        }
        
        # Sample callback data
        self.callback_data = {
            'Body': {
                'stkCallback': {
                    'MerchantRequestID': 'test-merchant-id',
                    'CheckoutRequestID': 'test-checkout-id',
                    'ResultCode': '0',
                    'ResultDesc': 'The service request is processed successfully.'
                }
            }
        }
    
    def test_stk_push_view(self):
        """Test STK Push view."""
        url = reverse('mpesastk:stk_push')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mpesastk/stk_push.html')
    
    @patch('apps.mpesastk.services.MPesaSTKService.initiate_stk_push')
    def test_stk_push_api(self, mock_initiate):
        """Test STK Push API."""
        # Mock the service response
        mock_transaction = MagicMock()
        mock_transaction.merchant_request_id = 'test-merchant-id'
        mock_transaction.checkout_request_id = 'test-checkout-id'
        mock_initiate.return_value = mock_transaction
        
        url = reverse('mpesastk:stk_push_api')
        response = self.client.post(
            url,
            data=self.transaction_data,
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        mock_initiate.assert_called_once()
    
    @patch('apps.mpesastk.services.MPesaSTKService.process_callback')
    def test_callback_view(self, mock_process):
        """Test callback processing."""
        # Mock the service response
        mock_transaction = MagicMock()
        mock_transaction.status = 'successful'
        mock_process.return_value = mock_transaction
        
        url = reverse('mpesastk:callback')
        response = self.client.post(
            url,
            data=self.callback_data,
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        mock_process.assert_called_once_with(self.callback_data)
    
    def test_transaction_list_view(self):
        """Test transaction list view."""
        # Create a test transaction
        STKTransaction.objects.create(
            merchant_request_id='test-merchant-id',
            checkout_request_id='test-checkout-id',
            amount=100,
            phone_number='254712345678',
            reference='TEST123',
            description='Test payment'
        )
        
        url = reverse('mpesastk:transactions')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'mpesastk/transaction_list.html')
        self.assertTrue(len(response.context['transactions']) > 0)
    
    def test_mpesa_service_password_generation(self):
        """Test MPesa password generation."""
        service = MPesaSTKService()
        password, timestamp = service._get_password()
        
        self.assertIsNotNone(password)
        self.assertTrue(len(password) > 0)
        self.assertTrue(len(timestamp) == 14)  # YYYYMMDDHHmmss
    
    @patch('requests.get')
    def test_mpesa_service_access_token(self, mock_get):
        """Test MPesa access token generation."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = {'access_token': 'test-token'}
        mock_get.return_value = mock_response
        
        service = MPesaSTKService()
        token = service._get_access_token()
        
        self.assertEqual(token, 'test-token')
        mock_get.assert_called_once()
    
    @patch('requests.post')
    def test_mpesa_service_query_status(self, mock_post):
        """Test MPesa query status."""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = self.mpesa_response
        mock_post.return_value = mock_response
        
        service = MPesaSTKService()
        result = service.query_stk_status('test-checkout-id')
        
        self.assertEqual(result, self.mpesa_response)
        mock_post.assert_called_once()
    
    def test_transaction_model_str(self):
        """Test transaction model string representation."""
        transaction = STKTransaction.objects.create(
            merchant_request_id='test-merchant-id',
            checkout_request_id='test-checkout-id',
            amount=100,
            phone_number='254712345678',
            reference='TEST123',
            description='Test payment'
        )
        
        expected_str = '254712345678 - 100 - pending'
        self.assertEqual(str(transaction), expected_str)
