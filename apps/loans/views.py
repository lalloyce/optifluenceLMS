from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count, Case, When, F, ExpressionWrapper, DecimalField, Value
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.exceptions import PermissionDenied, ValidationError
from decimal import Decimal, InvalidOperation

from .models import Loan, LoanProduct, LoanApplication, LoanGuarantor
from .forms import LoanForm, LoanApprovalForm
from apps.customers.models import Customer
import json
from datetime import timedelta, datetime

def generate_application_number():
    """Generate a unique loan application number."""
    prefix = timezone.now().strftime('%Y%m')
    last_loan = Loan.objects.filter(
        application_number__startswith=prefix
    ).order_by('-application_number').first()
    
    if last_loan:
        last_number = int(last_loan.application_number[-4:])
        new_number = str(last_number + 1).zfill(4)
    else:
        new_number = '0001'
    
    return f"{prefix}{new_number}"

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
        form = LoanForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.loan_officer = request.user
            loan.application_number = generate_application_number()
            loan.status = Loan.Status.PENDING
            
            # Handle guarantor if provided
            guarantor = form.cleaned_data.get('guarantor')
            if guarantor:
                loan_guarantor = LoanGuarantor(
                    loan=loan,
                    guarantor=guarantor,
                    guarantee_amount=loan.amount,  # You might want to adjust this
                    status='PENDING'
                )
                loan_guarantor.save()
            
            loan.save()
            messages.success(request, 'Loan application submitted successfully.')
            return redirect('web_loans:detail', pk=loan.pk)
    else:
        form = LoanForm()
    
    context = {
        'form': form,
        'loan_products': LoanProduct.objects.filter(is_active=True),
        'customers': Customer.objects.all()  # For guarantor selection
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
    
    context = {
        'loan': loan,
        'repayment_schedule': loan.repayment_schedule.all().order_by('installment_number')
    }
    return render(request, 'loans/loan_detail.html', context)

@login_required
def application_detail(request, pk):
    """Display detailed information about a loan application."""
    application = get_object_or_404(LoanApplication, pk=pk)
    
    if request.method == 'POST' and request.user.has_perm('loans.can_approve_loans'):
        action = request.POST.get('action')
        if action == 'approve':
            application.approve()
            loan = Loan.create_from_application(application, request.user)
            messages.success(request, 'Loan application approved successfully.')
            return redirect('web_loans:detail', pk=loan.pk)
        elif action == 'reject':
            reason = request.POST.get('rejection_reason')
            application.reject(reason)
            messages.success(request, 'Loan application rejected.')
        elif action == 'review':
            application.start_review(request.user)
            messages.success(request, 'Application review started.')
    
    context = {
        'application': application,
    }
    return render(request, 'loans/application_detail.html', context)

@login_required
def loan_approve(request, pk):
    """Handle loan approval process."""
    loan = get_object_or_404(Loan, pk=pk)
    
    if not request.user.has_perm('loans.can_approve_loans'):
        raise PermissionDenied
        
    if request.method == 'POST':
        form = LoanApprovalForm(request.POST, instance=loan)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.status = Loan.Status.APPROVED
            loan.approval_date = timezone.now()
            loan.save()
            messages.success(request, 'Loan approved successfully.')
            return redirect('web_loans:detail', pk=loan.pk)
    else:
        form = LoanApprovalForm(instance=loan)
    
    context = {
        'form': form,
        'loan': loan,
    }
    return render(request, 'loans/loan_approve.html', context)

@login_required
def loan_reject(request, pk):
    """Handle loan rejection."""
    loan = get_object_or_404(Loan, pk=pk)
    
    if not request.user.has_perm('loans.can_approve_loans'):
        raise PermissionDenied
        
    if request.method == 'POST':
        reason = request.POST.get('rejection_reason')
        loan.status = Loan.Status.REJECTED
        loan.notes = (loan.notes or '') + f"\nRejection Reason: {reason}"
        loan.save()
        messages.success(request, 'Loan rejected successfully.')
        return redirect('web_loans:detail', pk=loan.pk)
    
    return render(request, 'loans/loan_reject.html', {'loan': loan})

@login_required
def loan_disburse(request, pk):
    """Handle loan disbursement."""
    loan = get_object_or_404(Loan, pk=pk)
    
    if not request.user.has_perm('loans.can_disburse_loans'):
        raise PermissionDenied
        
    if loan.status != Loan.Status.APPROVED:
        messages.error(request, 'Only approved loans can be disbursed.')
        return redirect('web_loans:detail', pk=loan.pk)
        
    if request.method == 'POST':
        loan.status = Loan.Status.DISBURSED
        loan.disbursement_date = timezone.now()
        loan.maturity_date = loan.disbursement_date + timedelta(days=30 * loan.term_months)
        loan.save()
        
        # Generate repayment schedule
        loan.generate_repayment_schedule()
        
        messages.success(request, 'Loan disbursed successfully.')
        return redirect('web_loans:detail', pk=loan.pk)
    
    return render(request, 'loans/loan_disburse.html', {'loan': loan})

@login_required
def loan_calculator(request):
    """Loan calculator view."""
    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount', 0))
        term_months = int(request.POST.get('term_months', 0))
        interest_rate = Decimal(request.POST.get('interest_rate', 0))
        
        # Calculate monthly payment
        monthly_rate = interest_rate / 12 / 100
        monthly_payment = (amount * monthly_rate * (1 + monthly_rate) ** term_months) / ((1 + monthly_rate) ** term_months - 1)
        
        total_payment = monthly_payment * term_months
        total_interest = total_payment - amount
        
        return JsonResponse({
            'monthly_payment': float(monthly_payment),
            'total_payment': float(total_payment),
            'total_interest': float(total_interest)
        })
    
    return render(request, 'loans/loan_calculator.html')

@login_required
def loan_schedule(request, pk):
    """Display loan repayment schedule."""
    loan = get_object_or_404(Loan, pk=pk)
    schedule = loan.repayment_schedule.all().order_by('installment_number')
    
    context = {
        'loan': loan,
        'schedule': schedule,
    }
    return render(request, 'loans/loan_schedule.html', context)

@login_required
def loan_product_list(request):
    """List and manage loan products."""
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'delete':
            product_id = request.POST.get('product_id')
            try:
                product = LoanProduct.objects.get(id=product_id)
                product.delete()
                messages.success(request, f'Loan product "{product.name}" deleted successfully.')
            except LoanProduct.DoesNotExist:
                messages.error(request, 'Loan product not found.')
            except Exception as e:
                messages.error(request, f'Error deleting loan product: {str(e)}')
        else:
            # Handle create/update
            product_id = request.POST.get('product_id')
            try:
                if product_id:
                    # Update existing product
                    product = LoanProduct.objects.get(id=product_id)
                    message = f'Loan product "{product.name}" updated successfully.'
                else:
                    # Create new product
                    product = LoanProduct()
                    message = 'New loan product created successfully.'
                
                # Update product fields
                product.name = request.POST.get('name', '').strip()
                product.description = request.POST.get('description', '').strip()
                product.is_active = request.POST.get('is_active') == 'on'

                # Term and rates
                product.term_months = int(request.POST.get('term_months', 1))
                product.grace_period_months = int(request.POST.get('grace_period_months', 0))
                product.interest_rate = Decimal(request.POST.get('interest_rate', '0'))
                product.penalty_rate = Decimal(request.POST.get('penalty_rate', '0'))
                product.processing_fee = Decimal(request.POST.get('processing_fee', '0'))
                product.insurance_fee = Decimal(request.POST.get('insurance_fee', '0'))
                product.minimum_amount = Decimal(request.POST.get('minimum_amount', '0'))
                product.maximum_amount = Decimal(request.POST.get('maximum_amount', '0'))

                # Documents and criteria
                product.required_documents = request.POST.get('required_documents', '').strip()
                product.eligibility_criteria = request.POST.get('eligibility_criteria', '').strip()

                # Term limits
                product.minimum_term = 1
                product.maximum_term = product.term_months

                # Save the product
                product.save()

                # Update risk-based amounts
                if product.maximum_amount > 0:
                    product.high_risk_max_amount = product.maximum_amount * Decimal('0.3')
                    product.medium_risk_max_amount = product.maximum_amount * Decimal('0.6')
                    product.moderate_risk_max_amount = product.maximum_amount
                    product.save()
                
                messages.success(request, message)
            except LoanProduct.DoesNotExist:
                messages.error(request, 'Loan product not found.')
            except (ValueError, TypeError, InvalidOperation) as e:
                messages.error(request, f'Invalid value provided: {str(e)}')
            except Exception as e:
                messages.error(request, f'Error saving loan product: {str(e)}')
    
    # Get all loan products
    loan_products = LoanProduct.objects.all().order_by('-created_at')
    return render(request, 'loans/loan_product_list.html', {'loan_products': loan_products})
