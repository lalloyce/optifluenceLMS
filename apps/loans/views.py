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
from .models import Loan, LoanProduct, LoanApplication, LoanGuarantor, RepaymentSchedule
from .forms import LoanForm, LoanApprovalForm, LoanApplicationForm
from apps.customers.models import Customer
from .services.loan_services import apply_payment, record_payment as record_payment_service
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
    """Detailed dashboard view with more metrics."""
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

    active_loans = Loan.objects.filter(status=Loan.Status.DISBURSED)
    active_loans_count = active_loans.count()
    total_portfolio_value = active_loans.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
    week_ahead = today + timedelta(days=7)
    due_this_week = RepaymentSchedule.objects.filter(
        due_date__range=[today, week_ahead],
        status='PENDING'
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    overdue_amount = RepaymentSchedule.objects.filter(
        due_date__lt=today,
        status='PENDING'
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    recent_loans = Loan.objects.select_related('customer').filter(
        application_date__range=[start_date, end_date]
    ).order_by('-application_date')[:10]
    top_borrowers = Customer.objects.annotate(
        loan_count_all_time=Count('loans'),
        total_all_time=Sum('loans__amount')
    ).filter(
        loan_count_all_time__gt=0
    ).order_by('-total_all_time')[:10]
    loan_types = active_loans.values('loan_product__name').annotate(
        count=Count('id')
    ).order_by('-count')
    loan_types_labels = json.dumps([lt['loan_product__name'] for lt in loan_types])
    loan_types_data = json.dumps([lt['count'] for lt in loan_types])
    total_principal = active_loans.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
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
    monthly_disbursements = Loan.objects.filter(
        disbursement_date__range=[start_date, end_date],
        status=Loan.Status.DISBURSED
    ).extra(
        select={'month': "DATE_TRUNC('month', disbursement_date)"}
    ).values('month').annotate(
        total=Sum('amount')
    ).order_by('month')
    monthly_labels = json.dumps([d['month'].strftime('%B %Y') for d in monthly_disbursements])
    monthly_amounts = json.dumps([float(d['total']) for d in monthly_disbursements])

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
def customer_details_api(request, pk):
    """API endpoint for fetching customer details."""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    try:
        customer = Customer.objects.get(pk=pk)
        active_loans = Loan.objects.filter(
            customer=customer,
            status__in=[Loan.Status.APPROVED, Loan.Status.DISBURSED]
        ).select_related('loan_product')
        
        data = {
            'full_name': f"{customer.first_name} {customer.last_name}",
            'id_number': customer.id_number,
            'phone_number': customer.phone_number,
            'email': customer.email,
            'active_loans': [{
                'application_number': loan.application_number,
                'product_name': loan.loan_product.name,
                'amount': float(loan.amount),
                'status': loan.get_status_display()
            } for loan in active_loans]
        }
        return JsonResponse(data)
    except Customer.DoesNotExist:
        return JsonResponse({'error': 'Customer not found'}, status=404)

@login_required
def loan_application(request):
    """Handle new loan applications."""
    if not request.user.is_staff:
        messages.error(request, 'You do not have permission to create loan applications.')
        return redirect('web_accounts:login')

    if request.method == 'POST':
        form = LoanApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.created_by = request.user
            application.application_number = generate_application_number()
            application.status = LoanApplication.Status.SUBMITTED
            application.save()
            
            messages.success(request, 'Loan application submitted successfully!')
            return redirect('web_loans:application_detail', pk=application.pk)
    else:
        form = LoanApplicationForm()
        
        customer_id = request.GET.get('customer')
        if customer_id:
            try:
                customer = Customer.objects.get(id=customer_id)
                active_loans = Loan.objects.filter(
                    customer=customer,
                    status__in=[Loan.Status.APPROVED, Loan.Status.DISBURSED]
                ).select_related('loan_product')
                
                if active_loans.exists():
                    other_loans_info = "\n".join([
                        f"Loan #{loan.application_number}: {loan.loan_product.name} - "
                        f"Amount: {loan.amount}, Status: {loan.get_status_display()}"
                        for loan in active_loans
                    ])
                    form.initial['other_loans'] = other_loans_info
                else:
                    form.initial['other_loans'] = "No active loans"
            except Customer.DoesNotExist:
                pass
    
        context = {
        'form': form,
        'loan_products': LoanProduct.objects.filter(is_active=True),
        'customers': Customer.objects.filter(is_active=True)
    }
    return render(request, 'loans/loan_application.html', context)

@login_required
def guarantor_list_api(request):
    """API endpoint for fetching eligible guarantors."""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    customer_id = request.GET.get('exclude')
    if not customer_id:
        return JsonResponse({'error': 'Customer ID required'}, status=400)
    
    try:
        guarantors = Customer.objects.filter(
            is_active=True
        ).exclude(
            id=customer_id
        ).values('id', 'first_name', 'last_name', 'id_number')
        
        return JsonResponse({
            'guarantors': [{
                'id': g['id'],
                'name': f"{g['first_name']} {g['last_name']} - {g['id_number']}"
            } for g in guarantors]
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def loan_list(request):
    """List all loans with filtering options."""
    loans = Loan.objects.select_related('customer', 'loan_product', 'loan_officer')
    
    status = request.GET.get('status')
    if status:
        loans = loans.filter(status=status)
    
    search = request.GET.get('search')
    if search:
        loans = loans.filter(
            Q(customer__first_name__icontains=search) |
            Q(customer__last_name__icontains=search) |
            Q(application_number__icontains=search)
        )
    
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
        try:
            if action == 'approve':
                application.approve()
                loan = Loan.create_from_application(application, request.user)
                messages.success(request, 'Loan application approved and loan created successfully.')
                return redirect('web_loans:loan_detail', pk=loan.pk)
            elif action == 'reject':
                reason = request.POST.get('rejection_reason')
                application.reject(reason)
                messages.success(request, 'Loan application rejected.')
            elif action == 'review':
                application.start_review(request.user)
                messages.success(request, 'Application review started.')
        except ValueError as e:
            messages.error(request, str(e))
    
    remaining_balance = None
    if application.status == 'APPROVED' and hasattr(application, 'loan'):
        total_paid = sum(i.paid_amount for i in application.loan.repayment_schedule.all())
        remaining_balance = application.loan.amount - total_paid
    
    context = {
        'application': application,
        'remaining_balance': remaining_balance,
        'today': timezone.now(),
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
            return redirect('web_loans:loan_detail', pk=loan.pk)
    else:
        form = LoanApprovalForm(instance=loan)
    
    context = {
        'form': form,
        'loan': loan,
    }
    return render(request, 'loans/loan_approve.html', context)

@login_required
def guarantor_list_api(request):
    """API endpoint for fetching eligible guarantors."""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    
    customer_id = request.GET.get('exclude')
    if not customer_id:
        return JsonResponse({'error': 'Customer ID required'}, status=400)
    
    try:
        # Get all active customers except the loan applicant
        guarantors = Customer.objects.filter(
            is_active=True
        ).exclude(
            id=customer_id
        ).values('id', 'first_name', 'last_name', 'id_number')
        
        return JsonResponse({
            'guarantors': [{
                'id': g['id'],
                'name': f"{g['first_name']} {g['last_name']} - {g['id_number']}"
            } for g in guarantors]
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

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
        try:
            if action == 'approve':
                application.approve()
                loan = Loan.create_from_application(application, request.user)
                messages.success(request, 'Loan application approved and loan created successfully.')
                return redirect('web_loans:loan_detail', pk=loan.pk)
            elif action == 'reject':
                reason = request.POST.get('rejection_reason')
                application.reject(reason)
                messages.success(request, 'Loan application rejected.')
            elif action == 'review':
                application.start_review(request.user)
                messages.success(request, 'Application review started.')
        except ValueError as e:
            messages.error(request, str(e))
    
    # Calculate remaining balance if loan exists
    remaining_balance = None
    if application.status == 'APPROVED' and hasattr(application, 'loan'):
        total_paid = sum(i.paid_amount for i in application.loan.repayment_schedule.all())
        remaining_balance = application.loan.amount - total_paid
    
    context = {
        'application': application,
        'remaining_balance': remaining_balance,
        'today': timezone.now(),
    }
    return render(request, 'loans/application_detail.html', context)

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
        return redirect('web_loans:loan_detail', pk=loan.pk)
    
    return render(request, 'loans/loan_reject.html', {'loan': loan})

@login_required
def loan_disburse(request, pk):
    """Handle loan disbursement."""
    loan = get_object_or_404(Loan, pk=pk)
    
    if not request.user.has_perm('loans.can_disburse_loans'):
        raise PermissionDenied
        
    if loan.status != Loan.Status.APPROVED:
        messages.error(request, 'Only approved loans can be disbursed.')
        return redirect('web_loans:loan_detail', pk=loan.pk)

    # Handle search by National ID
    if request.method == 'GET':
        national_id = request.GET.get('national_id')
        if national_id:
            loan = Loan.objects.filter(customer__national_id=national_id).first()  # Adjust according to your model structure
            if loan:
                return render(request, 'loans/loan_disburse.html', {'loan': loan})
            else:
                messages.error(request, 'No loan found for this National ID.')
                return render(request, 'loans/loan_disburse.html', {'loan': None})    
    
    if request.method == 'POST':
        loan.status = Loan.Status.DISBURSED
        loan.disbursement_date = timezone.now()
        loan.maturity_date = loan.disbursement_date + timedelta(days=30 * loan.term_months)
        loan.save()
        
        # Generate repayment schedule
        loan.generate_repayment_schedule()
        
        messages.success(request, 'Loan disbursed successfully.')
        return redirect('web_loans:loan_detail', pk=loan.pk)
    
    return render(request, 'loans/loan_disburse.html', {'loan': loan})

@login_required
def record_payment(request, pk):
    """Record a payment for a loan installment."""
    from .models import Payment  # Import Payment within the function
    loan = get_object_or_404(Loan, pk=pk)
    
    if request.method == 'POST':
        installment_id = request.POST.get('installment_id')
        amount = Decimal(request.POST.get('amount'))
        payment_date = request.POST.get('payment_date')
        notes = request.POST.get('notes')
        
        try:
            installment = loan.repayment_schedule.get(id=installment_id)
            remaining = installment.total_amount - installment.paid_amount
            
            if amount > remaining:
                messages.error(request, f'Payment amount cannot exceed remaining amount of KES {remaining}')
            else:
                installment.paid_amount += amount
                installment.payment_date = payment_date
                if notes:
                    installment.notes = (installment.notes or '') + f'\n{timezone.now()}: {notes}'
                installment.save()
                installment.update_status()
                
                messages.success(request, f'Payment of KES {amount} recorded successfully')
        except RepaymentSchedule.DoesNotExist:
            messages.error(request, 'Invalid installment selected')
        except ValueError:
            messages.error(request, 'Invalid payment amount')
    
    return redirect('web_loans:application_detail', pk=loan.application.pk)
    
@login_required
def loan_calculator(request):
    """Loan calculator view."""
    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount', 0))
        term_months = int(request.POST.get('term_months', 0))
        interest_rate = Decimal(request.POST.get('interest_rate', 0))
        
        # Calculate simple interest
        annual_rate = interest_rate / 100
        total_interest = amount * annual_rate * (term_months / 12)
        total_payment = amount + total_interest
        monthly_payment = total_payment / term_months
        
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
                    product = LoanProduct.objects.get(id=product_id)
                    message = f'Loan product "{product.name}" updated successfully.'
                else:
                    product = LoanProduct()
                    message = 'New loan product created successfully.'
                
                product.name = request.POST.get('name', '').strip()
                product.description = request.POST.get('description', '').strip()
                product.is_active = request.POST.get('is_active') == 'on'
                product.term_months = int(request.POST.get('term_months', 1))
                product.grace_period_months = int(request.POST.get('grace_period_months', 0))
                product.interest_rate = Decimal(request.POST.get('interest_rate', '0'))
                product.penalty_rate = Decimal(request.POST.get('penalty_rate', '0'))
                product.processing_fee = Decimal(request.POST.get('processing_fee', '0'))
                product.insurance_fee = Decimal(request.POST.get('insurance_fee', '0'))
                product.minimum_amount = Decimal(request.POST.get('minimum_amount', '0'))
                product.maximum_amount = Decimal(request.POST.get('maximum_amount', '0'))
                product.required_documents = request.POST.get('required_documents', '').strip()
                product.eligibility_criteria = request.POST.get('eligibility_criteria', '').strip()
                product.minimum_term = 1
                product.maximum_term = product.term_months
                product.save()

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
    
    loan_products = LoanProduct.objects.all().order_by('-created_at')
    return render(request, 'loans/loan_product_list.html', {'loan_products': loan_products})

