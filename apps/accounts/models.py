"""
Custom User model using email as the unique identifier.

The User model extends Django's AbstractUser model to add a role field.

The UserManager is a custom manager for the User model.

The UserProfile model extends the User model to add additional profile information.

The UserProfile model has a one-to-one relationship with the User model.
"""
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    """Custom user model manager."""

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom User model using email as the unique identifier."""
    
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Administrator')
        LOAN_OFFICER = 'LOAN_OFFICER', _('Loan Officer')
        ACCOUNTANT = 'ACCOUNTANT', _('Accountant')
        MANAGER = 'MANAGER', _('Manager')
    
    username = None  # Remove username field
    email = models.EmailField(_('email address'), unique=True)
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.LOAN_OFFICER
    )
    is_email_verified = models.BooleanField(
        _('email verified'),
        default=False,
        help_text=_('Designates whether this user has verified their email address.')
    )
    email_verification_token = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text=_('Token for email verification')
    )
    email_verification_token_created = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('When the email verification token was created')
    )
    password_reset_token = models.CharField(max_length=100, blank=True, null=True)
    password_reset_token_created = models.DateTimeField(null=True, blank=True)
    
    # Make email the unique identifier
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    # Use custom manager
    objects = UserManager()
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
    
    def __str__(self):
        return self.email


class UserProfile(models.Model):
    """Extended profile information for users."""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    phone_number = models.CharField(max_length=20)
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    postal_code = models.CharField(max_length=20, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    hire_date = models.DateField()
    department = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    supervisor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='supervised_employees'
    )
    emergency_contact_name = models.CharField(max_length=255, null=True, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')
    
    def __str__(self):
        return f"Profile for {self.user.email}"


class AuditLog(models.Model):
    """Model to track user activities and system events."""
    
    class EventType(models.TextChoices):
        LOGIN = 'LOGIN', _('Login')
        LOGOUT = 'LOGOUT', _('Logout')
        LOGIN_FAILED = 'LOGIN_FAILED', _('Login Failed')
        PASSWORD_CHANGE = 'PASSWORD_CHANGE', _('Password Change')
        PASSWORD_RESET_REQUEST = 'PASSWORD_RESET_REQUEST', _('Password Reset Request')
        PASSWORD_RESET = 'PASSWORD_RESET', _('Password Reset')
        EMAIL_VERIFICATION = 'EMAIL_VERIFICATION', _('Email Verification')
        PROFILE_UPDATE = 'PROFILE_UPDATE', _('Profile Update')
        ROLE_CHANGE = 'ROLE_CHANGE', _('Role Change')
        ACCOUNT_CREATE = 'ACCOUNT_CREATE', _('Account Creation')
        ACCOUNT_DISABLE = 'ACCOUNT_DISABLE', _('Account Disabled')
        ACCOUNT_ENABLE = 'ACCOUNT_ENABLE', _('Account Enabled')
        MFA_ENABLE = 'MFA_ENABLE', _('MFA Enabled')
        MFA_DISABLE = 'MFA_DISABLE', _('MFA Disabled')
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs'
    )
    event_type = models.CharField(
        max_length=50,
        choices=EventType.choices
    )
    event_description = models.TextField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('SUCCESS', 'Success'),
            ('FAILURE', 'Failure'),
            ('WARNING', 'Warning'),
        ]
    )
    additional_data = models.JSONField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['event_type', '-created_at']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.event_type} - {self.user} - {self.created_at}"
