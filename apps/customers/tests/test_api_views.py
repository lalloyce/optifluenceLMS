"""Tests for customer API views."""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from apps.customers.models import Customer, BusinessProfile

User = get_user_model()

class CustomerAPITest(APITestCase):
    """Test cases for Customer API."""
    
    def setUp(self):
        """Set up test data."""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create test customers
        self.individual_customer = Customer.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone_number='254712345678',
            customer_type=Customer.CustomerType.INDIVIDUAL,
            created_by=self.user
        )
        
        self.business_customer = Customer.objects.create(
            first_name='Business',
            last_name='Owner',
            email='business@example.com',
            phone_number='254723456789',
            customer_type=Customer.CustomerType.BUSINESS,
            created_by=self.user
        )
        
        # Create business profile
        self.business_profile = BusinessProfile.objects.create(
            customer=self.business_customer,
            business_name='Test Business',
            business_type=BusinessProfile.BusinessType.LLC,
            primary_contact_name='Business Owner',
            primary_contact_position='CEO',
            primary_contact_phone='254723456789'
        )
    
    def test_list_customers(self):
        """Test retrieving customer list."""
        url = reverse('api_customers:customer-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_create_individual_customer(self):
        """Test creating individual customer."""
        url = reverse('api_customers:customer-list')
        data = {
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane@example.com',
            'phone_number': '254734567890',
            'customer_type': Customer.CustomerType.INDIVIDUAL
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 3)
        self.assertEqual(response.data['email'], 'jane@example.com')
    
    def test_create_business_customer(self):
        """Test creating business customer with profile."""
        url = reverse('api_customers:customer-list')
        data = {
            'first_name': 'New',
            'last_name': 'Business',
            'email': 'newbusiness@example.com',
            'phone_number': '254745678901',
            'customer_type': Customer.CustomerType.BUSINESS,
            'business_profile': {
                'business_name': 'New Test Business',
                'business_type': BusinessProfile.BusinessType.CORPORATION,
                'primary_contact_name': 'New Owner',
                'primary_contact_position': 'Manager',
                'primary_contact_phone': '254745678901'
            }
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customer.objects.count(), 3)
        self.assertEqual(BusinessProfile.objects.count(), 2)
    
    def test_verify_customer(self):
        """Test customer verification endpoint."""
        url = reverse('api_customers:customer-verify', args=[self.individual_customer.id])
        data = {'notes': 'Verified after document check'}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.individual_customer.refresh_from_db()
        self.assertEqual(
            self.individual_customer.verification_status,
            Customer.VerificationStatus.VERIFIED
        )
    
    def test_update_recommendations(self):
        """Test updating customer recommendations."""
        url = reverse('api_customers:customer-update-recommendations', 
                     args=[self.individual_customer.id])
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.individual_customer.refresh_from_db()
        self.assertIsNotNone(self.individual_customer.recommendation_score)
    
    def test_get_customer_insights(self):
        """Test retrieving customer insights."""
        url = reverse('api_customers:customer-insights', 
                     args=[self.individual_customer.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('profile_completion', response.data)
        self.assertIn('verification_status', response.data)
    
    def test_list_pending_verification(self):
        """Test listing customers pending verification."""
        url = reverse('api_customers:customer-pending-verification')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data['results'], list)

class BusinessProfileAPITest(APITestCase):
    """Test cases for BusinessProfile API."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.business_customer = Customer.objects.create(
            first_name='Business',
            last_name='Owner',
            email='business@example.com',
            phone_number='254723456789',
            customer_type=Customer.CustomerType.BUSINESS,
            created_by=self.user
        )
    
    def test_create_business_profile(self):
        """Test creating business profile."""
        url = reverse('api_customers:businessprofile-list')
        data = {
            'customer': self.business_customer.id,
            'business_name': 'Test Business',
            'business_type': BusinessProfile.BusinessType.LLC,
            'primary_contact_name': 'Business Owner',
            'primary_contact_position': 'CEO',
            'primary_contact_phone': '254723456789'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(BusinessProfile.objects.count(), 1)
    
    def test_create_profile_for_individual(self):
        """Test creating business profile for individual customer."""
        individual_customer = Customer.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone_number='254712345678',
            customer_type=Customer.CustomerType.INDIVIDUAL,
            created_by=self.user
        )
        
        url = reverse('api_customers:businessprofile-list')
        data = {
            'customer': individual_customer.id,
            'business_name': 'Test Business',
            'business_type': BusinessProfile.BusinessType.LLC,
            'primary_contact_name': 'John Doe',
            'primary_contact_position': 'Owner',
            'primary_contact_phone': '254712345678'
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
