"""
Django settings for OptifluenceLMS project.
"""

import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    
    # Third party apps
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    
    # Local apps
    'apps.accounts',
    'apps.customers',
    'apps.loans',
    'apps.transactions',
    'apps.mpesastk',
    'apps.core',  # Add core app
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',  
    'apps.accounts.middleware.SessionManagementMiddleware',
    'apps.core.middleware.RateLimitMiddleware',
    'apps.mpesastk.middleware.MPesaErrorMiddleware',  # Add MPesa error middleware
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': 'aws-0-eu-central-1.pooler.supabase.com',
        'NAME': 'postgres',
        'USER': 'postgres.tsgtzmqjrqimepiiuusm',
        'PASSWORD': os.getenv('SUPABASE_DB_PASSWORD', ''),
        'PORT': '6543',
        'OPTIONS': {
            'sslmode': 'require'
        }
    }
}

# Cache settings
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'django_cache_table',
    }
}

# Session settings
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1800  # 30 minutes in seconds
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

# JWT settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'SIGNING_KEY': os.getenv('SUPABASE_JWT_SECRET', SECRET_KEY),
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# CORS settings
CORS_ALLOW_ALL_ORIGINS = DEBUG
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',') if not DEBUG else []

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email settings
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.mailersend.net')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')

# Celery settings
CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
CELERY_RESULT_BACKEND = CELERY_BROKER_URL

# Authentication Backend
AUTHENTICATION_BACKENDS = [
    'apps.accounts.backends.EmailBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'SAMEORIGIN'
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = not DEBUG
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Session Security Settings
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_SAMESITE = 'Strict'

# Rate Limiting Settings
RATE_LIMITS = {
    'login': {'limit': 5, 'period': 300},  # 5 attempts per 5 minutes
    'register': {'limit': 3, 'period': 3600},  # 3 attempts per hour
    'password_reset': {'limit': 3, 'period': 3600},  # 3 attempts per hour
    'verify_email': {'limit': 3, 'period': 3600},  # 3 attempts per hour
}
RATELIMIT_ENABLE = True
RATELIMIT_USE_CACHE = 'default'
RATELIMIT_FAIL_OPEN = False

# Login URL settings
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'accounts:dashboard'
LOGOUT_REDIRECT_URL = 'accounts:login'

# Public URLs that don't require authentication
PUBLIC_URLS = [
    'accounts:login',
    'accounts:register',
    'accounts:password_reset',
    'accounts:password_reset_done',
    'accounts:password_reset_confirm',
    'accounts:password_reset_complete',
    'accounts:verify_email',
    'accounts:resend_verification',
    'admin:login',
]

# CSRF Settings
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'https://localhost:8000',
    'https://127.0.0.1:8000',
]

if not DEBUG:
    # In production, add your actual domain
    CSRF_TRUSTED_ORIGINS.extend([
        f"https://{host.strip()}" for host in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',')
        if host.strip()
    ])

# MPesa Settings
MPESA_ENVIRONMENT = os.getenv('MPESA_ENVIRONMENT', 'sandbox')
MPESA_CONSUMER_KEY = os.getenv('MPESA_CONSUMER_KEY')
MPESA_CONSUMER_SECRET = os.getenv('MPESA_CONSUMER_SECRET')
MPESA_SHORTCODE = os.getenv('MPESA_SHORTCODE')
MPESA_PASSKEY = os.getenv('MPESA_PASSKEY')
MPESA_CALLBACK_URL = os.getenv('MPESA_CALLBACK_URL')
MPESA_API_URL = 'https://sandbox.safaricom.co.ke' if MPESA_ENVIRONMENT == 'sandbox' else 'https://api.safaricom.co.ke'

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'optifluence.log'),
            'maxBytes': 1024*1024*5,  # 5 MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'propagate': True,
        },
        'django.request': {
            'handlers': ['mail_admins', 'file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'apps.accounts': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'apps.transactions': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
    }
}

# Create logs directory if it doesn't exist
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)
