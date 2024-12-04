"""Tests for customer services."""
from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.customers.models import Customer, BusinessProfile
from apps.customers.services import CustomerService

User = get_user_model()

class CustomerServiceTest(TestCase):
    """Test cases for CustomerService."""
    
    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create individual customer
        self.individual_customer = Customer.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone_number='254712345678',
            customer_type=Customer.CustomerType.INDIVIDUAL,
            credit_score=700
        )
        
        # Create business customer
        self.business_customer = Customer.objects.create(
            first_name='Business',
            last_name='Owner',
            email='business@example.com',
            phone_number='254723456789',
            customer_type=Customer.CustomerType.BUSINESS,
            credit_score=800
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
    
    def test_calculate_recommendation_score(self):
        """Test recommendation score calculation."""
        # Test individual customer score
        score = CustomerService.calculate_recommendation_score(self.individual_customer)
        self.assertIsInstance(score, float)
        self.assertTrue(0 <= score <= 100)
        
        # Test business customer score
        score = CustomerService.calculate_recommendation_score(self.business_customer)
        self.assertIsInstance(score, float)
        self.assertTrue(0 <= score <= 100)
    
    def test_get_recommended_products(self):
        """Test product recommendations."""
        # Test individual customer recommendations
        recommendations = CustomerService.get_recommended_products(self.individual_customer)
        self.assertIsInstance(recommendations, list)
        self.assertTrue(all(isinstance(r, dict) for r in recommendations))
        
        # Test business customer recommendations
        recommendations = CustomerService.get_recommended_products(self.business_customer)
        self.assertIsInstance(recommendations, list)
        self.assertTrue(all(isinstance(r, dict) for r in recommendations))
    
    def test_update_customer_recommendations(self):
        """Test updating customer recommendations."""
        # Update recommendations for individual customer
        CustomerService.update_customer_recommendations(self.individual_customer)
        self.individual_customer.refresh_from_db()
        self.assertIsNotNone(self.individual_customer.recommendation_score)
        self.assertIsNotNone(self.individual_customer.recommended_products)
        self.assertIsNotNone(self.individual_customer.last_recommendation_date)
        
        # Update recommendations for business customer
        CustomerService.update_customer_recommendations(self.business_customer)
        self.business_customer.refresh_from_db()
        self.assertIsNotNone(self.business_customer.recommendation_score)
        self.assertIsNotNone(self.business_customer.recommended_products)
        self.assertIsNotNone(self.business_customer.last_recommendation_date)
    
    def test_verify_customer(self):
        """Test customer verification."""
        notes = 'Verified after document check'
        CustomerService.verify_customer(
            customer=self.individual_customer,
            verified_by=self.user,
            notes=notes
        )
        
        self.individual_customer.refresh_from_db()
        self.assertEqual(
            self.individual_customer.verification_status,
            Customer.VerificationStatus.VERIFIED
        )
        self.assertEqual(self.individual_customer.verification_notes, notes)
        self.assertEqual(self.individual_customer.verified_by, self.user)
        self.assertIsNotNone(self.individual_customer.verified_at)
    
    def test_get_customer_insights(self):
        """Test getting customer insights."""
        insights = CustomerService.get_customer_insights(self.individual_customer)
        
        self.assertIsInstance(insights, dict)
        self.assertIn('profile_completion', insights)
        self.assertIn('active_loans_count', insights)
        self.assertIn('total_loan_amount', insights)
        self.assertIn('outstanding_amount', insights)
        self.assertIn('verification_status', insights)
    
    def test_calculate_profile_completion(self):
        """Test profile completion calculation."""
        completion = CustomerService._calculate_profile_completion(self.individual_customer)
        
        self.assertIsInstance(completion, float)
        self.assertTrue(0 <= completion <= 100)
