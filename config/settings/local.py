from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True

# Email backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
