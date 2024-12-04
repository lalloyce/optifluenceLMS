from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count, Case, When, F, ExpressionWrapper, DecimalField, Value
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.exceptions import PermissionDenied

from .models import Loan, LoanProduct, LoanDocument
from .forms import LoanApplicationForm, LoanApprovalForm, LoanDocumentForm
from apps.customers.models import Customer
from apps.transactions.models import RepaymentSchedule, Transaction
import json
from decimal import Decimal
from datetime import timedelta, datetime

@login_required
def loan_dashboard(request):
    """Dashboard view for loans."""
    context = {
        'pending_loans': Loan.objects.filter(status=Loan.Status.PENDING).count(),
        'approved_loans': Loan.objects.filter(status=Loan.Status.APPROVED).count(),
        'disbursed_loans': Loan.objects.filter(status=Loan.Status.DISBURSED).count(),
        'defaulted_loans': Loan.objects.filter(status=Loan.Status.DEFAULTED).count(),
    }
    return render(request, 'loans/dashboard.html', context)

@login_required
def dashboard(request):
    # Get time period from request
    period = request.GET.get('period', '30')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    today = timezone.now().date()
    
    if start_date and end_date and period == 'custom':
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        days = int(period)
        start_date = today - timedelta(days=days)
        end_date = today

    # KPI Metrics
    active_loans = Loan.objects.filter(status=Loan.Status.DISBURSED)
    active_loans_count = active_loans.count()
    total_portfolio_value = active_loans.aggregate(
        total=Sum('amount'))['total'] or Decimal('0.00')

    # Due this week
    week_ahead = today + timedelta(days=7)
    due_this_week = RepaymentSchedule.objects.filter(
        due_date__range=[today, week_ahead],
        status='PENDING'
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

    # Overdue amount
    overdue_amount = RepaymentSchedule.objects.filter(
        due_date__lt=today,
        status='PENDING'
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')

    # Recent Loans
    recent_loans = Loan.objects.select_related('customer').filter(
        application_date__range=[start_date, end_date]
    ).order_by('-application_date')[:10]

    # Top Borrowers - Calculate based on total loans taken
    top_borrowers = Customer.objects.annotate(
        loan_count_all_time=Count('loans'),
        total_all_time=Sum('loans__amount')
    ).filter(
        loan_count_all_time__gt=0
    ).order_by('-total_all_time')[:10]

    # Loan Type Distribution
    loan_types = active_loans.values('loan_product__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    loan_types_labels = json.dumps([lt['loan_product__name'] for lt in loan_types])
    loan_types_data = json.dumps([lt['count'] for lt in loan_types])

    # Portfolio Composition
    total_principal = active_loans.aggregate(
        total=Sum('amount'))['total'] or Decimal('0.00')
    total_interest = RepaymentSchedule.objects.filter(
        loan__status=Loan.Status.DISBURSED
    ).aggregate(
        total=Sum('interest_amount'))['total'] or Decimal('0.00')
    total_penalties = RepaymentSchedule.objects.filter(
        loan__status=Loan.Status.DISBURSED,
        due_date__lt=today,
        status='PENDING'
    ).aggregate(
        total=Sum('penalty_amount'))['total'] or Decimal('0.00')

    # Monthly Disbursement Trend
    monthly_disbursements = Loan.objects.filter(
        disbursement_date__range=[start_date, end_date],
        status=Loan.Status.DISBURSED
    ).extra(
        select={'month': "DATE_TRUNC('month', disbursement_date)"}
    ).values('month').annotate(
        total=Sum('amount')
    ).order_by('month')

    monthly_labels = json.dumps([
        d['month'].strftime('%B %Y') for d in monthly_disbursements
    ])
    monthly_amounts = json.dumps([
        float(d['total']) for d in monthly_disbursements
    ])

    context = {
        'days': int(period),
        'start_date': start_date,
        'end_date': end_date,
        'active_loans_count': active_loans_count,
        'total_portfolio_value': total_portfolio_value,
        'due_this_week': due_this_week,
        'overdue_amount': overdue_amount,
        'recent_loans': recent_loans,
        'top_borrowers': top_borrowers,
        'loan_types_labels': loan_types_labels,
        'loan_types_data': loan_types_data,
        'total_principal': float(total_principal),
        'total_interest': float(total_interest),
        'total_penalties': float(total_penalties),
        'monthly_labels': monthly_labels,
        'monthly_amounts': monthly_amounts,
    }

    return render(request, 'loans/dashboard.html', context)

@login_required
def loan_application(request):
    """Handle new loan applications."""
    if request.method == 'POST':
        form = LoanApplicationForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.loan_officer = request.user
            loan.status = Loan.Status.PENDING
            loan.save()
            messages.success(request, 'Loan application submitted successfully.')
            return redirect('loans:loan_detail', pk=loan.pk)
    else:
        form = LoanApplicationForm()
    
    context = {
        'form': form,
        'loan_products': LoanProduct.objects.filter(is_active=True),
    }
    return render(request, 'loans/loan_application.html', context)

@login_required
def loan_list(request):
    """List all loans with filtering options."""
    loans = Loan.objects.select_related('customer', 'loan_product', 'loan_officer')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        loans = loans.filter(status=status)
    
    # Search by customer name or loan number
    search = request.GET.get('search')
    if search:
        loans = loans.filter(
            Q(customer__first_name__icontains=search) |
            Q(customer__last_name__icontains=search) |
            Q(application_number__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(loans, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_choices': Loan.Status.choices,
    }
    return render(request, 'loans/loan_list.html', context)

@login_required
def loan_detail(request, pk):
    """Display detailed information about a loan."""
    loan = get_object_or_404(Loan, pk=pk)
    documents = loan.documents.all()
    
    if request.method == 'POST':
        doc_form = LoanDocumentForm(request.POST, request.FILES)
        if doc_form.is_valid():
            document = doc_form.save(commit=False)
            document.loan = loan
            document.uploaded_by = request.user
            document.save()
            messages.success(request, 'Document uploaded successfully.')
            return redirect('loans:loan_detail', pk=pk)
    else:
        doc_form = LoanDocumentForm()
    
    context = {
        'loan': loan,
        'documents': documents,
        'doc_form': doc_form,
    }
    return render(request, 'loans/loan_detail.html', context)

@login_required
def loan_create(request):
    """Create a new loan application."""
    if request.method == 'POST':
        form = LoanApplicationForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.loan_officer = request.user
            loan.status = Loan.Status.DRAFT
            loan.save()
            messages.success(request, 'New loan application created successfully.')
            return redirect('loans:loan_detail', pk=loan.pk)
    else:
        form = LoanApplicationForm()
    
    context = {
        'form': form,
        'loan_products': LoanProduct.objects.filter(is_active=True),
        'title': 'Create New Loan',
        'submit_text': 'Create Loan'
    }
    return render(request, 'loans/loan_form.html', context)

@login_required
def loan_edit(request, pk):
    """Edit an existing loan."""
    loan = get_object_or_404(Loan, pk=pk)
    
    # Check if user has permission to edit the loan
    if not request.user.has_perm('loans.change_loan'):
        raise PermissionDenied
    
    if request.method == 'POST':
        form = LoanApplicationForm(request.POST, instance=loan)
        if form.is_valid():
            form.save()
            messages.success(request, 'Loan updated successfully.')
            return redirect('loans:loans.detail', pk=loan.pk)
    else:
        form = LoanApplicationForm(instance=loan)
    
    context = {
        'form': form,
        'loan': loan,
        'title': 'Edit Loan',
    }
    return render(request, 'loans/loan_form.html', context)

@login_required
@require_http_methods(['POST'])
def loan_approve(request, pk):
    """Handle loan approval process."""
    loan = get_object_or_404(Loan, pk=pk)
    
    # Check if user has permission to approve loans
    if not request.user.has_perm('loans.can_approve_loans'):
        raise PermissionDenied
    
    form = LoanApprovalForm(request.POST)
    if form.is_valid():
        loan.status = Loan.Status.APPROVED
        loan.approval_date = timezone.now()
        loan.notes = form.cleaned_data['notes']
        loan.save()
        
        messages.success(request, 'Loan approved successfully.')
    else:
        messages.error(request, 'Error approving loan. Please check the form.')
    
    return redirect('loans:loan_detail', pk=pk)

@login_required
@require_http_methods(['POST'])
def loan_reject(request, pk):
    """Handle loan rejection."""
    loan = get_object_or_404(Loan, pk=pk)
    
    # Check if user has permission to reject loans
    if not request.user.has_perm('loans.can_approve_loans'):
        raise PermissionDenied
    
    notes = request.POST.get('notes', '')
    loan.status = Loan.Status.REJECTED
    loan.notes = notes
    loan.save()
    
    messages.success(request, 'Loan application rejected.')
    return redirect('loans:loan_detail', pk=pk)

@login_required
@require_http_methods(['POST'])
def loan_disburse(request, pk):
    """Handle loan disbursement."""
    loan = get_object_or_404(Loan, pk=pk)
    
    # Check if user has permission to disburse loans
    if not request.user.has_perm('loans.can_disburse_loans'):
        raise PermissionDenied
    
    if loan.status != Loan.Status.APPROVED:
        messages.error(request, 'Only approved loans can be disbursed.')
        return redirect('loans:loan_detail', pk=pk)
    
    loan.status = Loan.Status.DISBURSED
    loan.disbursement_date = timezone.now()
    loan.save()
    
    messages.success(request, 'Loan disbursed successfully.')
    return redirect('loans:loan_detail', pk=pk)

@login_required
def loan_documents(request, pk):
    """Handle loan document uploads and listing."""
    loan = get_object_or_404(Loan, pk=pk)
    
    if request.method == 'POST':
        form = LoanDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.loan = loan
            document.uploaded_by = request.user
            document.save()
            messages.success(request, 'Document uploaded successfully.')
            return redirect('loans:loans.documents', pk=loan.pk)
    else:
        form = LoanDocumentForm()
    
    documents = loan.documents.all()
    context = {
        'loan': loan,
        'form': form,
        'documents': documents,
        'title': 'Loan Documents',
    }
    return render(request, 'loans/loan_documents.html', context)

@login_required
@require_http_methods(['DELETE'])
def loan_document_delete(request, pk, doc_pk):
    """Delete a loan document."""
    document = get_object_or_404(LoanDocument, pk=doc_pk, loan_id=pk)
    
    # Only allow deletion by the uploader or staff
    if document.uploaded_by != request.user and not request.user.is_staff:
        raise PermissionDenied
    
    document.delete()
    return JsonResponse({'status': 'success'})

@login_required
@require_http_methods(['POST'])
def loan_delete(request, pk):
    """Delete a loan."""
    loan = get_object_or_404(Loan, pk=pk)
    
    # Check if user has permission to delete the loan
    if not request.user.has_perm('loans.delete_loan'):
        raise PermissionDenied
    
    # Only allow deletion of pending loans
    if loan.status != Loan.Status.PENDING:
        messages.error(request, 'Only pending loans can be deleted.')
        return redirect('loans:loans.detail', pk=loan.pk)
    
    loan.delete()
    messages.success(request, 'Loan deleted successfully.')
    return redirect('loans:loans.list')

@login_required
def loan_calculator(request):
    """Loan calculator view."""
    if request.method == 'POST':
        amount = float(request.POST.get('amount', 0))
        term = int(request.POST.get('term', 0))
        interest_rate = float(request.POST.get('interest_rate', 0))
        
        # Calculate monthly payment using the formula: PMT = P * (r * (1 + r)^n) / ((1 + r)^n - 1)
        monthly_rate = interest_rate / (12 * 100)
        monthly_payment = amount * (monthly_rate * (1 + monthly_rate)**term) / ((1 + monthly_rate)**term - 1)
        
        total_payment = monthly_payment * term
        total_interest = total_payment - amount
        
        return JsonResponse({
            'monthly_payment': round(monthly_payment, 2),
            'total_payment': round(total_payment, 2),
            'total_interest': round(total_interest, 2)
        })
    
    return render(request, 'loans/loan_calculator.html')

@login_required
def loan_schedule(request, pk):
    """Display loan repayment schedule."""
    loan = get_object_or_404(Loan, pk=pk)
    
    # Get all repayment schedules for this loan
    schedules = loan.repayment_schedule.all().order_by('due_date')
    
    context = {
        'loan': loan,
        'schedules': schedules,
        'title': 'Repayment Schedule',
    }
    return render(request, 'loans/loan_schedule.html', context)
