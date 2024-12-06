from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods, require_POST
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.core.mail import send_mail
from django.utils import timezone
from datetime import datetime, timedelta, date
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from .models import User, UserProfile, AuditLog
from .forms import CustomUserCreationForm, PasswordResetRequestForm, SetNewPasswordForm, UserProfileForm
from .audit import log_event
from django.db.models import Count, Sum, Avg
from django.db.models.functions import TruncMonth
from apps.loans.models import Loan
from apps.transactions.models import Transaction, RepaymentSchedule
from apps.customers.models import Customer
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.core.cache import cache
from functools import wraps
import time
from decimal import Decimal
from .services import EmailService, UserService
from django.utils.safestring import mark_safe

def validate_password(password):
    """Validate password strength."""
    errors = []
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    if not any(char.islower() for char in password):
        errors.append("Password must contain at least one lowercase letter.")
    if not any(char.isupper() for char in password):
        errors.append("Password must contain at least one uppercase letter.")
    if not any(char.isdigit() for char in password):
        errors.append("Password must contain at least one digit.")
    if not any(char in '!@#$%^&*()_+-=[]{};\':\"|<>?,./`~' for char in password):
        errors.append("Password must contain at least one special character.")
    return errors

def rate_limit(key_prefix, limit=5, period=300):
    """
    Rate limiting decorator that allows `limit` requests per `period` seconds
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Create a unique key based on IP and prefix
            key = f"ratelimit:{key_prefix}:{request.META.get('REMOTE_ADDR', '')}"
            
            # Get the current count and timestamp
            cache_data = cache.get(key, {'count': 0, 'timestamp': time.time()})
            
            # Reset count if period has passed
            if time.time() - cache_data['timestamp'] > period:
                cache_data = {'count': 0, 'timestamp': time.time()}
            
            # Increment count
            cache_data['count'] += 1
            cache.set(key, cache_data, period)
            
            # Check if limit exceeded
            if cache_data['count'] > limit:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Too many attempts. Please try again later.'
                }, status=429)
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

@csrf_exempt  # Temporary! Remove after testing
@require_http_methods(["GET", "POST"])
def login_view(request):
    """User login view."""
    # If user is already authenticated, redirect to dashboard
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')

    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user = authenticate(request, email=email, password=password)
        
        if user is not None and user.is_active:
            login(request, user)
            return redirect('accounts:dashboard')
        else:
            messages.error(request, 'Invalid email or password.')
    
    return render(request, 'accounts/login.html', {'title': 'Login'})

@login_required(login_url='accounts:login')
def logout_view(request):
    """User logout view."""
    user = request.user
    log_event(
        request,
        AuditLog.EventType.LOGOUT,
        f"User logged out",
        user=user,
        status='SUCCESS'
    )
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')

@csrf_protect
@require_http_methods(["GET", "POST"])
def register_view(request):
    """User registration view."""
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        try:
            email = form.data.get('email')
            if User.objects.filter(email=email).exists():
                messages.error(request, "This email address is already in use.")
                return render(request, 'accounts/register.html', {'form': form})

            if form.is_valid():
                user = UserService.create_user(form)
                try:
                    EmailService.send_verification_email(request, user)
                    messages.success(request, 'Registration successful! Please check your email to verify your account.')
                    return redirect('accounts:login')
                except Exception as e:
                    messages.error(request, 'Failed to send verification email. Please try again or contact support.')
                    user.delete()  # Roll back user creation if email fails
                    return redirect('accounts:register')
            else:
                for field in form.errors:
                    for error in form.errors[field]:
                        messages.error(request, f'{field}: {error}')
        except Exception as e:
            messages.error(request, f'An error occurred during registration: {str(e)}')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

@csrf_protect
@rate_limit('password_reset', limit=3, period=3600)  # 3 attempts per hour
@require_http_methods(["GET", "POST"])
def password_reset_view(request):
    """Password reset view."""
    if request.method == "POST":
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                token = generate_token()
                user.password_reset_token = token
                user.password_reset_token_created = timezone.now()
                user.save()
                
                send_password_reset_email(request, user)
                
                log_event(
                    request,
                    AuditLog.EventType.PASSWORD_RESET_REQUEST,
                    f"Password reset requested",
                    user=user,
                    status='SUCCESS'
                )
                
                messages.success(
                    request,
                    'Password reset instructions have been sent to your email.'
                )
                return redirect('accounts:login')
            except User.DoesNotExist:
                log_event(
                    request,
                    AuditLog.EventType.PASSWORD_RESET_REQUEST,
                    f"Password reset attempted for non-existent email: {email}",
                    status='FAILURE',
                    additional_data={'reason': 'email_not_found'}
                )
                messages.error(
                    request,
                    'No account found with this email address.'
                )
    else:
        form = PasswordResetRequestForm()
    return render(request, 'accounts/password_reset.html', {'form': form})

@csrf_protect
@require_http_methods(["GET", "POST"])
def password_reset_confirm(request, token):
    """Confirm password reset view."""
    try:
        user = User.objects.get(
            password_reset_token=token,
            password_reset_token_created__gte=timezone.now() - timedelta(hours=24)
        )
        
        if request.method == "POST":
            form = SetNewPasswordForm(request.POST)
            if form.is_valid():
                user.set_password(form.cleaned_data['password'])
                user.password_reset_token = None
                user.password_reset_token_created = None
                user.save()
                
                log_event(
                    request,
                    AuditLog.EventType.PASSWORD_RESET,
                    f"Password reset completed",
                    user=user,
                    status='SUCCESS'
                )
                
                messages.success(request, 'Your password has been reset successfully. You can now login with your new password.')
                return redirect('accounts:login')
        else:
            form = SetNewPasswordForm()
            
        return render(request, 'accounts/password_reset_confirm.html', {'form': form})
        
    except User.DoesNotExist:
        log_event(
            request,
            AuditLog.EventType.PASSWORD_RESET,
            f"Password reset attempted with invalid token",
            status='FAILURE',
            additional_data={'token': token}
        )
        messages.error(request, 'Invalid or expired password reset link.')
        return redirect('accounts:password_reset')

@login_required(login_url='accounts:login')
def profile_view(request):
    """User profile view."""
    if request.method == "POST":
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save()
            
            log_event(
                request,
                AuditLog.EventType.PROFILE_UPDATE,
                f"User profile updated",
                user=user,
                status='SUCCESS',
                additional_data={
                    'updated_fields': list(form.changed_data)
                }
            )
            
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('accounts:profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'accounts/profile.html', {'form': form})

@login_required(login_url='accounts:login')
def settings_view(request):
    """View for user settings."""
    return render(request, 'accounts/settings.html', {
        'page_title': 'Settings',
        'active_tab': 'settings'
    })

from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

@login_required(login_url='accounts:login')
@require_POST
def keep_alive(request):
    """
    Endpoint to keep the session alive through AJAX calls
    """
    return JsonResponse({'status': 'ok'})

@require_POST
def send_email(request):
    try:
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        if not all([name, email, subject, message]):
            messages.error(request, 'All fields are required.')
            return redirect('home')

        # Compose email message with HTML formatting
        html_message = f"""
        <html>
        <body>
            <h3>New Contact Form Submission</h3>
            <p><strong>From:</strong> {name} ({email})</p>
            <p><strong>Subject:</strong> {subject}</p>
            <p><strong>Message:</strong></p>
            <p>{message}</p>
        </body>
        </html>
        """

        # Plain text version
        text_message = f"""
        New Contact Form Submission

        From: {name} ({email})
        Subject: {subject}

        Message:
        {message}
        """

        try:
            # Send email
            send_mail(
                subject=f"Contact Form: {subject}",
                message=text_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['optifluence@gmail.com'],
                html_message=html_message,
                fail_silently=False
            )
            messages.success(request, 'Your message has been sent successfully!')
        except Exception as e:
            print(f"Email sending error: {str(e)}")  # For debugging
            messages.error(request, 'An error occurred while sending your message. Please try again later.')

        return redirect('home')

    except Exception as e:
        print(f"Form processing error: {str(e)}")  # For debugging
        messages.error(request, 'An error occurred while processing your request. Please try again later.')
        return redirect('home')

def generate_token():
    return secrets.token_urlsafe(32)

def send_password_reset_email(request, user):
    token = generate_token()
    user.password_reset_token = token
    user.password_reset_token_created = timezone.now()
    user.save()

    reset_url = request.build_absolute_uri(
        reverse('accounts:password_reset_confirm', kwargs={'token': token})
    )

    # Render email template
    html_message = render_to_string('emails/password_reset.html', {
        'user': user,
        'reset_url': reset_url,
    })
    plain_message = strip_tags(html_message)

    # Send email
    send_mail(
        'Password Reset Request - OptifluenceLMS',
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )

def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
                send_password_reset_email(request, user)
                messages.success(
                    request,
                    'If an account exists with this email, you will receive password reset instructions.'
                )
            except User.DoesNotExist:
                # Use the same message to prevent email enumeration
                messages.success(
                    request,
                    'If an account exists with this email, you will receive password reset instructions.'
                )
            return redirect('accounts:login')
    else:
        form = PasswordResetRequestForm()
    
    return render(request, 'accounts/password_reset_request.html', {'form': form})

def password_reset_confirm(request, token):
    try:
        user = User.objects.get(password_reset_token=token)
        
        # Check if token is expired (15 minutes)
        token_age = timezone.now() - user.password_reset_token_created
        if token_age > timedelta(minutes=15):
            messages.error(request, 'Password reset link has expired. Please request a new one.')
            return redirect('accounts:password_reset_request')
        
        if request.method == 'POST':
            form = SetNewPasswordForm(request.POST)
            if form.is_valid():
                # Set new password
                user.set_password(form.cleaned_data['password'])
                user.password_reset_token = None
                user.password_reset_token_created = None
                user.save()
                
                messages.success(request, 'Your password has been successfully reset. You can now log in with your new password.')
                return redirect('accounts:login')
        else:
            form = SetNewPasswordForm()
        
        return render(request, 'accounts/password_reset_confirm.html', {'form': form})
        
    except User.DoesNotExist:
        messages.error(request, 'Invalid password reset link.')
        return redirect('accounts:login')

@login_required(login_url='accounts:login')
def dashboard_view(request):
    """Main dashboard view that requires authentication"""
    try:
        # Get the current date in the current timezone
        today = timezone.now().date()
        
        # Calculate start and end dates
        period = request.GET.get('period', '30')
        end_date = timezone.now()
        start_date = end_date - timedelta(days=int(period))
        
        # Make sure all datetime objects are timezone-aware
        if isinstance(start_date, datetime) and timezone.is_naive(start_date):
            start_date = timezone.make_aware(start_date)
        if isinstance(end_date, datetime) and timezone.is_naive(end_date):
            end_date = timezone.make_aware(end_date)
        
        # Initialize context with basic data
        context = {
            'title': 'Dashboard',
            'user': request.user,
            'days': int(period),
            'start_date': start_date,
            'end_date': end_date,
        }

        try:
            # Loan Statistics
            loan_stats = {
                'total_loans': Loan.objects.count(),
                'active_loans': Loan.objects.filter(status='DISBURSED').count(),
                'pending_loans': Loan.objects.filter(status='PENDING').count(),
                'defaulted_loans': Loan.objects.filter(status='DEFAULTED').count(),
                'total_portfolio': Loan.objects.filter(status='DISBURSED').aggregate(
                    total=Sum('amount'))['total'] or Decimal('0.00'),
                'total_disbursed': Loan.objects.filter(
                    status='DISBURSED',
                    disbursement_date__range=[start_date, end_date]
                ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00'),
            }
            context['loan_stats'] = loan_stats
        except Exception as e:
            messages.warning(request, 'Unable to load loan statistics.')
            context['loan_stats'] = {}

        try:
            # Recent Loans
            context['recent_loans'] = Loan.objects.select_related('customer').order_by(
                '-application_date'
            )[:10]
        except Exception as e:
            messages.warning(request, 'Unable to load recent loans.')
            context['recent_loans'] = []

        try:
            # Recent Transactions
            context['recent_transactions'] = Transaction.objects.select_related(
                'loan', 'loan__customer'
            ).order_by('-created_at')[:10]
        except Exception as e:
            messages.warning(request, 'Unable to load recent transactions.')
            context['recent_transactions'] = []

        try:
            # Top Borrowers
            context['top_borrowers'] = Customer.objects.annotate(
                loan_count=Count('loans'),
                total_amount=Sum('loans__amount')
            ).filter(
                loan_count__gt=0
            ).order_by('-total_amount')[:10]
        except Exception as e:
            messages.warning(request, 'Unable to load top borrowers.')
            context['top_borrowers'] = []

        try:
            # Monthly Disbursement Trend
            context['monthly_disbursements'] = Loan.objects.filter(
                disbursement_date__range=[start_date, end_date],
                status='DISBURSED'
            ).annotate(
                month=TruncMonth('disbursement_date')
            ).values('month').annotate(
                total=Sum('amount')
            ).order_by('month')
        except Exception as e:
            messages.warning(request, 'Unable to load monthly disbursements.')
            context['monthly_disbursements'] = []

        # Add URLs
        try:
            context.update({
                'transactions_url': reverse('web_transactions:list'),
                'loans_url': reverse('web_loans:list')
            })
        except Exception as e:
            # If URL reverse fails, don't let it break the dashboard
            messages.warning(request, 'Some navigation links may be unavailable.')

        # Add audit log for dashboard access
        try:
            log_event(
                request,
                AuditLog.EventType.LOGIN,
                f"User accessed dashboard",
                user=request.user,
                status='SUCCESS',
                additional_data={
                    'period': period,
                    'start_date': str(start_date),
                    'end_date': str(end_date)
                }
            )
        except Exception as e:
            # Don't let audit logging failure affect the dashboard
            pass

        return render(request, 'accounts/dashboard.html', context)
        
    except Exception as e:
        # If there's a critical error, render a basic dashboard instead of redirecting
        messages.error(request, 'Some dashboard features are temporarily unavailable.')
        context = {
            'title': 'Dashboard',
            'user': request.user,
            'error': True
        }
        return render(request, 'accounts/dashboard.html', context)

@login_required(login_url='accounts:login')
def reports_view(request):
    """Generate and display various reports."""
    # Get date range from request or default to current month
    start_date = request.GET.get('start_date', timezone.now().replace(day=1))
    end_date = request.GET.get('end_date', timezone.now())
    
    # Loan statistics
    loan_stats = {
        'total_loans': Loan.objects.count(),
        'active_loans': Loan.objects.filter(status='DISBURSED').count(),
        'pending_loans': Loan.objects.filter(status='PENDING').count(),
        'defaulted_loans': Loan.objects.filter(status='DEFAULTED').count(),
    }
    
    # Monthly loan disbursements
    monthly_disbursements = (
        Loan.objects.filter(status='DISBURSED')
        .annotate(month=TruncMonth('disbursement_date'))
        .values('month')
        .annotate(count=Count('id'), total_amount=Sum('amount'))
        .order_by('-month')[:12]
    )
    
    # Transaction statistics
    transaction_stats = {
        'total_repayments': Transaction.objects.filter(
            transaction_type='REPAYMENT',
            status='COMPLETED'
        ).aggregate(
            count=Count('id'),
            total_amount=Sum('amount')
        ),
        'monthly_collections': Transaction.objects.filter(
            transaction_type='REPAYMENT',
            status='COMPLETED'
        ).annotate(
            month=TruncMonth('transaction_date')
        ).values('month').annotate(
            total_amount=Sum('amount')
        ).order_by('-month')[:12]
    }
    
    context = {
        'loan_stats': loan_stats,
        'monthly_disbursements': monthly_disbursements,
        'transaction_stats': transaction_stats,
        'start_date': start_date,
        'end_date': end_date,
        'title': 'Reports Dashboard'
    }
    return render(request, 'accounts/reports.html', context)

@csrf_protect
def verify_email(request, token):
    """Email verification view."""
    try:
        user = UserService.verify_email(token)
        messages.success(request, 'Email verified successfully! You can now log in.')
        return redirect('accounts:login')
    except User.DoesNotExist:
        log_event(
            request,
            AuditLog.EventType.EMAIL_VERIFICATION,
            f"Email verification failed - invalid token",
            status='FAILURE',
            additional_data={'token': token}
        )
        messages.error(request, 'Invalid verification link. Please request a new one.')
        return redirect('accounts:resend_verification')
    except ValueError as e:
        log_event(
            request,
            AuditLog.EventType.EMAIL_VERIFICATION,
            f"Email verification failed - {str(e)}",
            status='FAILURE',
            additional_data={'token': token}
        )
        messages.error(request, 'Verification link has expired. Please request a new one.')
        return redirect('accounts:resend_verification')
    except Exception as e:
        log_event(
            request,
            AuditLog.EventType.EMAIL_VERIFICATION,
            f"Email verification error",
            status='FAILURE',
            additional_data={'error': str(e)}
        )
        messages.error(request, 'An error occurred during verification. Please try again.')
        return redirect('accounts:login')

@csrf_protect
def resend_verification_email(request):
    """Resend verification email view."""
    if request.method == "POST":
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            
            if user.is_email_verified:
                messages.info(request, 'This email address has already been verified.')
                return redirect('accounts:login')
            
            # Check if last email was sent within 2 minutes
            if user.email_verification_token_created:
                time_since_last_email = timezone.now() - user.email_verification_token_created
                if time_since_last_email < timedelta(minutes=2):
                    messages.warning(request, 'Please wait a few minutes before requesting another verification email.')
                    return redirect('accounts:resend_verification')
            
            try:
                EmailService.send_verification_email(request, user)
                messages.success(request, 'Verification email sent! Please check your inbox.')
                log_event(
                    request,
                    AuditLog.EventType.EMAIL_VERIFICATION,
                    f"Verification email resent",
                    user=user,
                    status='SUCCESS'
                )
                return redirect('accounts:login')
            except Exception as e:
                log_event(
                    request,
                    AuditLog.EventType.EMAIL_VERIFICATION,
                    f"Failed to resend verification email",
                    user=user,
                    status='FAILURE',
                    additional_data={'error': str(e)}
                )
                messages.error(request, 'Failed to send verification email. Please try again later.')
                
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email address.')
            log_event(
                request,
                AuditLog.EventType.EMAIL_VERIFICATION,
                f"Verification email resend attempt for non-existent user",
                status='FAILURE',
                additional_data={'email': email}
            )
    
    return render(request, 'accounts/resend_verification.html')
