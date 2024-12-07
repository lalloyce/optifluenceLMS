import logging
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.db.models.functions import TruncMonth
import json
from datetime import date, datetime, timedelta

logger = logging.getLogger(__name__)

class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)

from .models import Customer, BusinessProfile
from .forms import (
    CustomerBasicForm, CustomerAddressForm, CustomerIdentityForm,
    CustomerEmploymentForm, BusinessProfileForm
)

# Create your views here.

@login_required
def customer_list(request):
    """List all customers with search and filtering."""
    search_query = request.GET.get('q', '')
    customers = Customer.objects.all().order_by('-created_at')
    
    if search_query:
        customers = customers.filter(
            Q(full_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )
    
    paginator = Paginator(customers, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'customers': page_obj,
        'search_query': search_query,
        'title': 'Customer List'
    }
    return render(request, 'customers/customer_list.html', context)

@login_required
def customer_create(request):
    """Multi-step form for creating a new customer."""
    current_step = request.session.get('customer_creation_step', 1)
    form_data = request.session.get('customer_form_data', {})
    
    logger.info(f"Starting customer_create view. Current step: {current_step}")
    logger.info(f"Session form_data: {form_data}")
    
    if request.method == 'POST':
        action = request.POST.get('action')
        logger.info(f"POST request received. Action: {action}")
        logger.info(f"POST data: {request.POST}")
        
        if action == 'next':
            logger.info("Processing 'next' action")
            if current_step == 1:
                form = CustomerBasicForm(request.POST)
            elif current_step == 2:
                form = CustomerAddressForm(request.POST)
            elif current_step == 3:
                form = CustomerIdentityForm(request.POST)
            elif current_step == 4:
                form = CustomerEmploymentForm(request.POST)
            elif current_step == 5 and form_data.get('customer_type') == Customer.CustomerType.BUSINESS:
                form = BusinessProfileForm(request.POST)
            
            if form.is_valid():
                logger.info("Form is valid")
                # Convert form data to dict and handle date objects
                step_data = form.cleaned_data
                form_data.update(step_data)
                
                # Store the serialized data in session
                json_data = json.dumps(form_data, cls=DateEncoder)
                request.session['customer_form_data'] = json.loads(json_data)
                logger.info(f"Updated form_data: {form_data}")
                
                # Check if we're at the final step
                is_business = form_data.get('customer_type') == Customer.CustomerType.BUSINESS
                is_final_step = (current_step == 4 and not is_business) or \
                               (current_step == 5 and is_business)
                
                if is_final_step:
                    logger.info("Final step - creating customer")
                    try:
                        # Create the customer
                        customer_data = form_data.copy()
                        if is_business:
                            # Remove business profile fields from customer data
                            business_fields = BusinessProfileForm.Meta.fields
                            business_data = {k: customer_data.pop(k) for k in business_fields if k in customer_data}
                        
                        customer = Customer.objects.create(**customer_data)
                        
                        if is_business:
                            BusinessProfile.objects.create(customer=customer, **business_data)
                        
                        # Clear session data
                        del request.session['customer_creation_step']
                        del request.session['customer_form_data']
                        
                        messages.success(request, 'Customer created successfully.')
                        return redirect('web_customers:detail', pk=customer.pk)
                    except Exception as e:
                        logger.error(f"Error creating customer: {str(e)}")
                        messages.error(request, f"Error creating customer: {str(e)}")
                else:
                    logger.info(f"Moving to next step: {current_step + 1}")
                    request.session['customer_creation_step'] = current_step + 1
                    return redirect('web_customers:create')
            else:
                logger.error(f"Form validation failed. Errors: {form.errors}")
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
        
        elif action == 'previous' and current_step > 1:
            logger.info(f"Moving to previous step: {current_step - 1}")
            request.session['customer_creation_step'] = current_step - 1
            return redirect('web_customers:create')
    
    # Determine which form to show
    logger.info(f"Preparing form for step {current_step}")
    if current_step == 1:
        form = CustomerBasicForm(initial=form_data)
    elif current_step == 2:
        form = CustomerAddressForm(initial=form_data)
    elif current_step == 3:
        form = CustomerIdentityForm(initial=form_data)
    elif current_step == 4:
        form = CustomerEmploymentForm(initial=form_data)
    elif current_step == 5 and form_data.get('customer_type') == Customer.CustomerType.BUSINESS:
        form = BusinessProfileForm(initial=form_data)
    else:
        form = CustomerBasicForm(initial=form_data)
    
    is_business = form_data.get('customer_type') == Customer.CustomerType.BUSINESS
    context = {
        'form': form,
        'current_step': current_step,
        'total_steps': 5 if is_business else 4,
        'title': 'Create New Customer',
        'submit_text': 'Create Customer'
    }
    logger.info(f"Rendering form with context: {context}")
    return render(request, 'customers/customer_form.html', context)

@login_required
def customer_detail(request, pk):
    """Display detailed customer information."""
    customer = get_object_or_404(Customer, pk=pk)
    
    # Get customer service for insights
    from .services import CustomerService
    insights = CustomerService.get_customer_insights(customer)
    
    # Get loans and guarantor information
    loans = customer.loans.all().order_by('-created_at')
    guaranteed_loans = customer.guaranteed_loans.select_related('loan', 'loan__customer').order_by('-created_at')
    loan_guarantors = customer.loans.first().guarantors.select_related('guarantor') if customer.loans.exists() else []
    
    # Update recommendations if needed
    if not customer.recommendation_score or \
       (customer.last_recommendation_date and 
        (timezone.now() - customer.last_recommendation_date).days >= 7):
        CustomerService.update_customer_recommendations(customer)
    
    # Prepare loan repayment data for charts
    loan_data = []
    for loan in loans:
        # Get all installments for this loan
        installments = loan.installment_set.all().order_by('due_date').select_related('loan')
        payments = loan.payment_set.all().order_by('payment_date').select_related(
            'loan', 'transaction', 'transaction__mpesa_payment'
        )
        
        # Calculate monthly expected vs actual payments
        monthly_data = {
            'loan_id': loan.id,
            'loan_reference': loan.reference_number,
            'amount': float(loan.amount),
            'disbursement_date': loan.disbursement_date.strftime('%Y-%m-%d'),
            'term_months': loan.term_months,
            'interest_rate': float(loan.interest_rate),
            'installments': [],
            'payments': []
        }
        
        # Add installment data
        for installment in installments:
            monthly_data['installments'].append({
                'due_date': installment.due_date.strftime('%Y-%m-%d'),
                'amount': float(installment.amount),
                'principal': float(installment.principal_amount),
                'interest': float(installment.interest_amount),
                'penalties': float(installment.penalty_amount or 0),
                'status': installment.status,
                'installment_number': installment.installment_number,
                'days_overdue': (timezone.now().date() - installment.due_date).days if installment.status == 'Overdue' else 0
            })
        
        # Add payment data
        for payment in payments:
            payment_data = {
                'payment_date': payment.payment_date.strftime('%Y-%m-%d'),
                'amount': float(payment.amount),
                'payment_method': payment.payment_method,
                'reference': payment.reference_number,
                'status': payment.status,
                'notes': payment.notes or '',
                'created_at': payment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'created_by': payment.created_by.get_full_name() if payment.created_by else 'System',
                'transaction_type': 'Manual',
                'allocations': [
                    {
                        'installment_number': alloc.installment.installment_number,
                        'amount': float(alloc.amount),
                        'allocation_type': alloc.allocation_type,
                        'created_at': alloc.created_at.strftime('%Y-%m-%d %H:%M:%S')
                    } for alloc in payment.paymentallocation_set.all().select_related('installment')
                ],
                'documents': [
                    {
                        'name': doc.name,
                        'file_type': doc.file_type,
                        'uploaded_at': doc.uploaded_at.strftime('%Y-%m-%d %H:%M:%S'),
                        'uploaded_by': doc.uploaded_by.get_full_name() if doc.uploaded_by else 'System',
                        'file_url': doc.file.url if doc.file else None
                    } for doc in payment.documents.all().select_related('uploaded_by')
                ],
                'audit_trail': [
                    {
                        'action': log.action,
                        'timestamp': log.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                        'user': log.user.get_full_name() if log.user else 'System',
                        'details': log.details
                    } for log in payment.auditlog_set.all().select_related('user').order_by('-timestamp')
                ]
            }
            
            # Add MPesa payment details if available
            if payment.transaction and payment.transaction.mpesa_payment:
                mpesa = payment.transaction.mpesa_payment
                payment_data.update({
                    'transaction_type': 'MPesa',
                    'mpesa_receipt': mpesa.receipt_number,
                    'mpesa_phone': mpesa.phone_number,
                    'mpesa_name': mpesa.first_name + ' ' + mpesa.last_name,
                    'mpesa_time': mpesa.transaction_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'mpesa_status': mpesa.result_desc
                })
            
            monthly_data['payments'].append(payment_data)
        
        loan_data.append(monthly_data)
    
    context = {
        'customer': customer,
        'loans': loans,
        'guaranteed_loans': guaranteed_loans,
        'loan_guarantors': loan_guarantors,
        'profile_completion': insights['profile_completion'],
        'loan_data': json.dumps(loan_data),
        'title': f'Customer: {customer.get_full_name()}'
    }
    return render(request, 'customers/customer_detail.html', context)

@login_required
def customer_edit(request, pk):
    """Edit customer information."""
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'POST':
        basic_form = CustomerBasicForm(request.POST, instance=customer)
        address_form = CustomerAddressForm(request.POST, instance=customer)
        identity_form = CustomerIdentityForm(request.POST, instance=customer)
        employment_form = CustomerEmploymentForm(request.POST, instance=customer)
        
        if customer.is_business:
            business_form = BusinessProfileForm(request.POST, instance=customer.business_profile)
            forms_valid = all([basic_form.is_valid(), address_form.is_valid(), 
                             identity_form.is_valid(), employment_form.is_valid(),
                             business_form.is_valid()])
        else:
            forms_valid = all([basic_form.is_valid(), address_form.is_valid(), 
                             identity_form.is_valid(), employment_form.is_valid()])
        
        if forms_valid:
            basic_form.save()
            address_form.save()
            identity_form.save()
            employment_form.save()
            if customer.is_business:
                business_form.save()
            messages.success(request, 'Customer information updated successfully.')
            return redirect('web_customers:customers.detail', pk=customer.pk)
    else:
        basic_form = CustomerBasicForm(instance=customer)
        address_form = CustomerAddressForm(instance=customer)
        identity_form = CustomerIdentityForm(instance=customer)
        employment_form = CustomerEmploymentForm(instance=customer)
        business_form = BusinessProfileForm(instance=customer.business_profile) if customer.is_business else None
    
    context = {
        'basic_form': basic_form,
        'address_form': address_form,
        'identity_form': identity_form,
        'employment_form': employment_form,
        'business_form': business_form,
        'customer': customer,
        'title': f'Edit Customer: {customer.full_name}',
        'submit_text': 'Update Customer'
    }
    return render(request, 'customers/customer_form.html', context)

@login_required
def customer_delete(request, pk):
    """Delete a customer."""
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'POST':
        customer.delete()
        messages.success(request, 'Customer deleted successfully.')
        return redirect('web_customers:customers.list')
    
    context = {
        'customer': customer,
        'title': f'Delete Customer: {customer.full_name}',
    }
    return render(request, 'customers/customer_confirm_delete.html', context)
