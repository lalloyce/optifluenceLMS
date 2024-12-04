from django.views.generic import CreateView, DetailView, ListView
from django.views.generic.edit import FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.utils.translation import gettext as _
from django.contrib import messages
from django.db.models import Q

from ..models import Loan, RepaymentSchedule, Transaction
from ..forms.repayment import RepaymentForm, WaivePenaltyForm
from ..services.repayment import RepaymentService

class RepaymentCreateView(LoginRequiredMixin, CreateView):
    """View for creating new loan repayments."""
    
    form_class = RepaymentForm
    template_name = 'loans/repayment/create.html'
    
    def get_loan(self):
        return get_object_or_404(
            Loan.objects.select_related('customer'),
            pk=self.kwargs['loan_id'],
            status=Loan.Status.DISBURSED
        )
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['loan'] = self.get_loan()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        loan = self.get_loan()
        context['loan'] = loan
        
        # Get repayment schedules
        context['schedules'] = loan.repayment_schedule.all()
        
        # Get recent transactions
        context['recent_transactions'] = loan.transactions.filter(
            transaction_type__in=[
                Transaction.Type.REPAYMENT,
                Transaction.Type.PENALTY
            ]
        ).order_by('-created_at')[:5]
        
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            _('Payment of %(amount)s has been processed successfully') % {
                'amount': form.cleaned_data['amount']
            }
        )
        return response
    
    def get_success_url(self):
        return reverse_lazy(
            'loans:loan_detail',
            kwargs={'pk': self.kwargs['loan_id']}
        )


class WaivePenaltyView(LoginRequiredMixin, FormView):
    """View for waiving penalties on a repayment schedule."""
    
    form_class = WaivePenaltyForm
    template_name = 'loans/repayment/waive_penalty.html'
    
    def get_schedule(self):
        return get_object_or_404(
            RepaymentSchedule.objects.select_related('loan'),
            pk=self.kwargs['schedule_id'],
            loan__status=Loan.Status.DISBURSED
        )
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['schedule'] = self.get_schedule()
        kwargs['user'] = self.request.user
        return kwargs
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        schedule = self.get_schedule()
        context['schedule'] = schedule
        context['loan'] = schedule.loan
        return context
    
    def form_valid(self, form):
        transaction = form.save()
        messages.success(
            self.request,
            _('Penalty of %(amount)s has been waived successfully') % {
                'amount': form.cleaned_data['amount']
            }
        )
        return super().form_valid(form)
    
    def get_success_url(self):
        schedule = self.get_schedule()
        return reverse_lazy(
            'loans:loan_detail',
            kwargs={'pk': schedule.loan.id}
        )


class RepaymentScheduleView(LoginRequiredMixin, DetailView):
    """View for displaying loan repayment schedule."""
    
    model = Loan
    template_name = 'loans/repayment/schedule.html'
    context_object_name = 'loan'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get repayment schedules with transactions
        schedules = self.object.repayment_schedule.prefetch_related(
            'transactions'
        ).order_by('due_date')
        
        # Calculate penalties for overdue schedules
        repayment_service = RepaymentService(self.object)
        for schedule in schedules:
            if schedule.is_overdue:
                schedule.current_penalty = repayment_service.calculate_penalty(schedule)
        
        context['schedules'] = schedules
        context['balance'] = repayment_service.get_loan_balance()
        
        return context


class TransactionListView(LoginRequiredMixin, ListView):
    """View for listing loan transactions."""
    
    model = Transaction
    template_name = 'loans/repayment/transactions.html'
    context_object_name = 'transactions'
    paginate_by = 20
    
    def get_queryset(self):
        loan = get_object_or_404(Loan, pk=self.kwargs['loan_id'])
        return loan.transactions.select_related(
            'loan',
            'repayment_schedule',
            'processed_by'
        ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        loan = get_object_or_404(Loan, pk=self.kwargs['loan_id'])
        context['loan'] = loan
        
        # Get transaction summary
        summary = {
            'total_paid': loan.transactions.filter(
                transaction_type=Transaction.Type.REPAYMENT,
                status=Transaction.Status.COMPLETED
            ).aggregate(total=models.Sum('amount'))['total'] or 0,
            'total_penalties': loan.transactions.filter(
                transaction_type=Transaction.Type.PENALTY,
                status=Transaction.Status.COMPLETED
            ).aggregate(total=models.Sum('amount'))['total'] or 0,
            'total_waivers': loan.transactions.filter(
                transaction_type=Transaction.Type.WAIVER,
                status=Transaction.Status.COMPLETED
            ).aggregate(total=models.Sum('amount'))['total'] or 0
        }
        context['summary'] = summary
        
        return context


def get_loan_balance(request, loan_id):
    """AJAX view to get current loan balance."""
    if not request.is_ajax():
        return JsonResponse({'error': 'Invalid request'}, status=400)
        
    try:
        loan = Loan.objects.get(pk=loan_id)
        repayment_service = RepaymentService(loan)
        balance = repayment_service.get_loan_balance()
        
        return JsonResponse({
            'success': True,
            'balance': balance
        })
    except Loan.DoesNotExist:
        return JsonResponse({
            'error': 'Loan not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)
