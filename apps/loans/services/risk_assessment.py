from decimal import Decimal
from datetime import datetime, timedelta
from django.db.models import Sum, Count, Q, F, Max
from apps.loans.models import Loan
from apps.transactions.models import RepaymentSchedule, Transaction

class LoanRiskAssessment:
    """Service class for assessing loan risk and calculating credit scores."""
    
    def __init__(self, customer, loan_amount=None):
        self.customer = customer
        self.loan_amount = loan_amount
        self.risk_factors = {}
        self.score = 0
        
    def calculate_risk_score(self):
        """Calculate overall risk score based on multiple factors."""
        self._assess_payment_history()
        self._assess_loan_history()
        self._assess_loan_amount_risk()
        self._assess_active_loans()
        
        # Calculate weighted score
        weights = {
            'payment_history': 0.40,  # Increased weight for payment history
            'loan_history': 0.30,     # Increased weight for loan history
            'loan_amount': 0.15,      # Slight increase for amount assessment
            'active_loans': 0.15      # New factor for concurrent loans
        }
        
        self.score = sum(
            self.risk_factors[factor] * weights[factor]
            for factor in weights.keys()
        )
        
        return self.score
    
    def _assess_payment_history(self):
        """Assess customer's payment history."""
        past_loans = Loan.objects.filter(
            customer=self.customer,
            status__in=[Loan.Status.CLOSED, Loan.Status.DEFAULTED]
        )
        
        total_payments = RepaymentSchedule.objects.filter(
            loan__in=past_loans
        ).count()
        
        late_payments = RepaymentSchedule.objects.filter(
            loan__in=past_loans,
            status='PAID',
            paid_date__gt=F('due_date')
        ).count()
        
        defaulted_payments = RepaymentSchedule.objects.filter(
            loan__in=past_loans,
            status='DEFAULTED'
        ).count()
        
        if total_payments > 0:
            on_time_ratio = 1 - ((late_payments + defaulted_payments * 2) / total_payments)
            score = min(100, on_time_ratio * 100)
        else:
            score = 50  # Neutral score for new customers
            
        self.risk_factors['payment_history'] = score
        
    def _assess_loan_history(self):
        """Assess customer's loan history."""
        past_loans = Loan.objects.filter(customer=self.customer)
        
        completed_loans = past_loans.filter(status=Loan.Status.CLOSED).count()
        defaulted_loans = past_loans.filter(status=Loan.Status.DEFAULTED).count()
        total_loans = past_loans.count()
        
        if total_loans > 0:
            success_ratio = completed_loans / total_loans
            default_penalty = (defaulted_loans / total_loans) * 50
            score = min(100, (success_ratio * 100) - default_penalty)
            
            # Bonus points for consistent good history
            if completed_loans >= 3 and defaulted_loans == 0:
                score = min(100, score + 10)
        else:
            score = 50  # Neutral score for new customers
            
        self.risk_factors['loan_history'] = score
        
    def _assess_loan_amount_risk(self):
        """Assess risk based on requested loan amount."""
        if not self.loan_amount:
            self.risk_factors['loan_amount'] = 50
            return
            
        # Compare with previous loans
        max_previous_loan = Loan.objects.filter(
            customer=self.customer,
            status=Loan.Status.CLOSED
        ).aggregate(max_amount=Max('amount'))['max_amount'] or 0
        
        if max_previous_loan == 0:
            # First time borrower
            self.risk_factors['loan_amount'] = 50
            return
            
        amount_increase_ratio = float(self.loan_amount) / max_previous_loan
        
        # Score based on amount increase ratio
        if amount_increase_ratio <= 1.0:  # Same or less than previous
            score = 100
        elif amount_increase_ratio <= 1.5:
            score = 80
        elif amount_increase_ratio <= 2.0:
            score = 60
        elif amount_increase_ratio <= 3.0:
            score = 40
        else:
            score = 20
            
        self.risk_factors['loan_amount'] = score
        
    def _assess_active_loans(self):
        """Assess risk based on number and status of active loans."""
        active_loans = Loan.objects.filter(
            customer=self.customer,
            status=Loan.Status.DISBURSED
        )
        
        active_count = active_loans.count()
        
        # Check for late payments in active loans
        late_payments = RepaymentSchedule.objects.filter(
            loan__in=active_loans,
            status='PENDING',
            due_date__lt=datetime.now()
        ).count()
        
        # Base score on number of active loans
        if active_count == 0:
            score = 100
        elif active_count == 1:
            score = 75
        elif active_count == 2:
            score = 50
        else:
            score = 25
            
        # Penalty for late payments in active loans
        if late_payments > 0:
            score = max(0, score - (late_payments * 15))
            
        self.risk_factors['active_loans'] = score
        
    def get_risk_assessment_summary(self):
        """Get detailed summary of risk assessment."""
        if not self.risk_factors:
            self.calculate_risk_score()
            
        risk_levels = {
            (80, 100): ('Low Risk', 'text-green-600'),
            (60, 79): ('Moderate Risk', 'text-yellow-600'),
            (40, 59): ('Medium Risk', 'text-orange-600'),
            (0, 39): ('High Risk', 'text-red-600')
        }
        
        risk_level = next(
            (level for (min_score, max_score), level in risk_levels.items()
             if min_score <= self.score <= max_score),
            ('Unknown Risk', 'text-gray-600')
        )
        
        return {
            'score': round(self.score, 2),
            'risk_level': risk_level[0],
            'risk_color': risk_level[1],
            'factors': {
                'Payment History': round(self.risk_factors['payment_history'], 2),
                'Loan History': round(self.risk_factors['loan_history'], 2),
                'Loan Amount': round(self.risk_factors['loan_amount'], 2),
                'Active Loans': round(self.risk_factors['active_loans'], 2)
            },
            'details': {
                'completed_loans': Loan.objects.filter(
                    customer=self.customer,
                    status=Loan.Status.CLOSED
                ).count(),
                'active_loans': Loan.objects.filter(
                    customer=self.customer,
                    status=Loan.Status.DISBURSED
                ).count(),
                'defaulted_loans': Loan.objects.filter(
                    customer=self.customer,
                    status=Loan.Status.DEFAULTED
                ).count()
            }
        }
