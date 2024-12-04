"""Transaction views."""
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from django.views.generic import DetailView, ListView, CreateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from apps.core.views import (
    BaseListView, BaseCreateView, BaseUpdateView, BaseDeleteView
)
from .models import Transaction
from .forms import TransactionForm
from .services import TransactionService

@method_decorator(login_required, name='dispatch')
class TransactionListView(ListView):
    """List all transactions with search and filtering."""
    model = Transaction
    template_name = 'transactions/transaction_list.html'
    context_object_name = 'transactions'
    title = 'Transaction List'
    paginate_by = 10
    
    def get_queryset(self):
        """Get transactions queryset."""
        search_query = self.request.GET.get('q', '')
        transactions = super().get_queryset().select_related(
            'loan', 'processed_by'
        ).order_by('-transaction_date')
        
        if search_query:
            transactions = transactions.filter(
                Q(reference_number__icontains=search_query) |
                Q(loan__application_number__icontains=search_query) |
                Q(loan__customer__full_name__icontains=search_query)
            )
        
        return transactions
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context

@method_decorator(login_required, name='dispatch')
class TransactionCreateView(CreateView):
    """Create a new transaction."""
    model = Transaction
    form_class = TransactionForm
    template_name = 'transactions/transaction_form.html'
    title = 'Record New Transaction'
    
    def form_valid(self, form):
        """Process valid form."""
        try:
            transaction = TransactionService.create_transaction(
                loan=form.cleaned_data['loan'],
                amount=form.cleaned_data['amount'],
                transaction_type=form.cleaned_data['transaction_type'],
                user=self.request.user,
                description=form.cleaned_data.get('description')
            )
            messages.success(self.request, 'Transaction recorded successfully.')
            return redirect('transactions:detail', pk=transaction.pk)
        except Exception as e:
            messages.error(self.request, f'Error creating transaction: {str(e)}')
            return self.form_invalid(form)

@method_decorator(login_required, name='dispatch')
class TransactionDetailView(DetailView):
    """Display detailed transaction information."""
    model = Transaction
    template_name = 'transactions/transaction_detail.html'
    context_object_name = 'transaction'
    
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
