from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone

from ..models import Loan
from ..services.repayment import RepaymentService

class LoanDetailView(LoginRequiredMixin, DetailView):
    model = Loan
    template_name = 'loans/loan_detail.html'
    context_object_name = 'loan'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        loan = self.get_object()
        
        # Get repayment service
        repayment_service = RepaymentService(loan)
        
        # Get loan balance
        context['balance'] = repayment_service.get_loan_balance()
        
        # Get recent transactions (last 5)
        context['recent_transactions'] = loan.transactions.order_by('-created_at')[:5]
        
        # Get next payment if loan is active
        if loan.status == Loan.Status.DISBURSED:
            next_payment = loan.repayment_schedule.filter(
                status__in=['PENDING', 'PARTIALLY_PAID', 'OVERDUE']
            ).order_by('due_date').first()
            
            if next_payment:
                # Calculate days overdue if applicable
                if next_payment.is_overdue:
                    next_payment.days_overdue = (timezone.now().date() - next_payment.due_date).days
                
                context['next_payment'] = next_payment
        
        return context
