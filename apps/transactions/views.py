"""Transaction views."""
from django.shortcuts import render
from django.views.generic import ListView, CreateView, DetailView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Transaction
from .forms import TransactionForm
from apps.loans.models import Loan
from django.contrib import messages
from django.utils import timezone

class TransactionListView(LoginRequiredMixin, ListView):
    """List all transactions with search and filtering."""
    model = Transaction
    template_name = 'transactions/transaction_list.html'
    context_object_name = 'transactions'
    paginate_by = 10
    ordering = ['-transaction_date']

class TransactionCreateView(LoginRequiredMixin, CreateView):
    """Create a new transaction."""
    model = Transaction
    form_class = TransactionForm
    template_name = 'transactions/transaction_form.html'
    success_url = reverse_lazy('web_transactions:list')

    def form_valid(self, form):
        """Process valid form."""
        form.instance.processed_by = self.request.user
        form.instance.status = 'COMPLETED'  # Auto-complete the transaction
        response = super().form_valid(form)
        
        # Add success message
        messages.success(self.request, 'Transaction recorded successfully.')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Record Transaction'
        return context

@login_required
def load_loans(request):
    """AJAX view to load loans for a selected customer."""
    customer_id = request.GET.get('customer_id')
    print(f"Loading loans for customer ID: {customer_id}")
    
    if customer_id:
        loans = Loan.objects.filter(
            customer_id=customer_id,
            status='DISBURSED'
        ).select_related('customer')
        
        print(f"Found {loans.count()} disbursed loans")
        
        loan_data = [
            {
                'id': loan.id,
                'text': f'Loan #{loan.id} - KES {loan.amount:,.2f}'
            }
            for loan in loans
        ]
        print(f"Loan data: {loan_data}")
        
        return JsonResponse({'loans': loan_data})
    return JsonResponse({'loans': []})

@method_decorator(login_required, name='dispatch')
class TransactionDetailView(DetailView):
    """Display detailed transaction information."""
    model = Transaction
    template_name = 'transactions/transaction_detail.html'
    context_object_name = 'transaction'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Transaction Details - {self.object.reference_number}'
        return context

    def get_title(self):
        """Get page title."""
        return f'Transaction: {self.object.reference_number}'

@method_decorator(login_required, name='dispatch')
class TransactionReverseView(DetailView):
    """Reverse a transaction."""
    model = Transaction
    template_name = 'transactions/transaction_reverse.html'
    context_object_name = 'transaction'
    
    def post(self, request, *args, **kwargs):
        """Handle POST request."""
        transaction = self.get_object()
        
        if transaction.status != Transaction.Status.COMPLETED:
            messages.error(request, 'Only completed transactions can be reversed.')
            return redirect('transactions:detail', pk=transaction.pk)
        
        try:
            reversal = TransactionService.reverse_transaction(transaction, request.user)
            messages.success(request, 'Transaction reversed successfully.')
            return redirect('transactions:detail', pk=reversal.pk)
        except Exception as e:
            messages.error(request, f'Error reversing transaction: {str(e)}')
            return redirect('transactions:detail', pk=transaction.pk)
    
    def get_title(self):
        """Get page title."""
        return f'Reverse Transaction: {self.object.reference_number}'
