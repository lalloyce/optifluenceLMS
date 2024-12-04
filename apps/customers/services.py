"""Customer management services."""
from datetime import datetime, timedelta
from typing import List, Dict, Any
from django.db.models import Q, F, Count, Avg
from django.utils import timezone
from .models import Customer, BusinessProfile

class CustomerService:
    """Service class for customer-related operations."""
    
    @staticmethod
    def calculate_recommendation_score(customer: Customer) -> float:
        """
        Calculate recommendation score based on various factors.
        
        Factors considered:
        - Payment history
        - Credit score
        - Transaction volume
        - Account age
        - Document verification status
        """
        score = 50.0  # Base score
        
        # Credit score contribution (up to 20 points)
        if customer.credit_score:
            score += min((customer.credit_score - 300) / 550 * 20, 20)
        
        # Verification status contribution (up to 10 points)
        if customer.verification_status == Customer.VerificationStatus.VERIFIED:
            score += 10
        
        # Document verification (up to 10 points)
        verified_docs = customer.documents.filter(is_verified=True).count()
        score += min(verified_docs * 2, 10)
        
        # Loan history (up to 10 points)
        active_loans = customer.get_active_loans().count()
        if active_loans > 0:
            score -= min(active_loans * 2, 10)  # Reduce score for multiple active loans
        
        return min(max(score, 0), 100)  # Ensure score is between 0 and 100

    @staticmethod
    def get_recommended_products(customer: Customer) -> List[Dict[str, Any]]:
        """Get personalized product recommendations for customer."""
        recommendations = []
        score = customer.recommendation_score or 0
        
        # Basic recommendations based on customer type and score
        if customer.is_business:
            if score >= 80:
                recommendations.append({
                    'type': 'business_loan',
                    'name': 'Premium Business Loan',
                    'max_amount': 1000000,
                    'interest_rate': 12.5,
                    'term_months': 24
                })
            elif score >= 60:
                recommendations.append({
                    'type': 'business_loan',
                    'name': 'Standard Business Loan',
                    'max_amount': 500000,
                    'interest_rate': 14.0,
                    'term_months': 18
                })
            else:
                recommendations.append({
                    'type': 'business_loan',
                    'name': 'Starter Business Loan',
                    'max_amount': 100000,
                    'interest_rate': 15.5,
                    'term_months': 12
                })
        else:
            if score >= 80:
                recommendations.append({
                    'type': 'personal_loan',
                    'name': 'Premium Personal Loan',
                    'max_amount': 500000,
                    'interest_rate': 13.5,
                    'term_months': 24
                })
            elif score >= 60:
                recommendations.append({
                    'type': 'personal_loan',
                    'name': 'Standard Personal Loan',
                    'max_amount': 250000,
                    'interest_rate': 15.0,
                    'term_months': 18
                })
            else:
                recommendations.append({
                    'type': 'personal_loan',
                    'name': 'Basic Personal Loan',
                    'max_amount': 50000,
                    'interest_rate': 16.5,
                    'term_months': 12
                })
        
        return recommendations

    @staticmethod
    def update_customer_recommendations(customer: Customer) -> None:
        """Update customer's recommendation score and products."""
        score = CustomerService.calculate_recommendation_score(customer)
        recommendations = CustomerService.get_recommended_products(customer)
        
        customer.recommendation_score = score
        customer.recommended_products = recommendations
        customer.last_recommendation_date = timezone.now()
        customer.save()

    @staticmethod
    def verify_customer(customer: Customer, verified_by: Any, notes: str = '') -> None:
        """Verify a customer's profile."""
        customer.verification_status = Customer.VerificationStatus.VERIFIED
        customer.verification_notes = notes
        customer.verified_by = verified_by
        customer.verified_at = timezone.now()
        customer.save()

    @staticmethod
    def get_customers_requiring_verification() -> List[Customer]:
        """Get list of customers requiring verification."""
        return Customer.objects.filter(
            verification_status=Customer.VerificationStatus.PENDING,
            documents__is_verified=True  # Has at least one verified document
        ).distinct()

    @staticmethod
    def get_customer_insights(customer: Customer) -> Dict[str, Any]:
        """Get insights about a customer's profile and activity."""
        active_loans = customer.get_active_loans()
        loan_history = customer.get_loan_history()
        
        return {
            'profile_completion': CustomerService._calculate_profile_completion(customer),
            'active_loans_count': active_loans.count(),
            'total_loan_amount': customer.get_total_loan_amount(),
            'outstanding_amount': customer.get_total_outstanding_amount(),
            'average_loan_amount': loan_history.aggregate(avg=Avg('amount'))['avg'],
            'recommendation_score': customer.recommendation_score,
            'verification_status': customer.verification_status,
            'last_activity': customer.updated_at,
        }

    @staticmethod
    def _calculate_profile_completion(customer: Customer) -> float:
        """Calculate the completion percentage of a customer's profile."""
        required_fields = ['first_name', 'last_name', 'phone_number', 'email']
        optional_fields = ['date_of_birth', 'address', 'city', 'state', 
                         'postal_code', 'country', 'id_type', 'id_number']
        
        # Count filled required fields
        filled_required = sum(1 for field in required_fields 
                            if getattr(customer, field))
        
        # Count filled optional fields
        filled_optional = sum(1 for field in optional_fields 
                            if getattr(customer, field))
        
        # Calculate weighted completion percentage
        required_weight = 0.7
        optional_weight = 0.3
        
        required_completion = (filled_required / len(required_fields)) * required_weight
        optional_completion = (filled_optional / len(optional_fields)) * optional_weight
        
        return (required_completion + optional_completion) * 100
