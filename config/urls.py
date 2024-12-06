"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.contrib.auth.decorators import login_required
from apps.accounts import views as account_views

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Frontend URLs
    path('', account_views.login_view, name='home'),
    path('reports/', login_required(account_views.reports_view), name='reports'),
    
    # Non-API account URLs
    path('accounts/', include('apps.accounts.urls')),
    
    # Main app URLs
    path('customers/', include('apps.customers.urls', namespace='web_customers')),
    path('loans/', include('apps.loans.urls', namespace='web_loans')),
    path('transactions/', include('apps.transactions.urls', namespace='web_transactions')),
    
    # API endpoints (temporarily disabled)
    # path('api/v1/customers/', include('apps.customers.api_urls', namespace='api_customers')),
    # path('api/v1/loans/', include('apps.loans.api_urls', namespace='api_loans')),
    # path('api/v1/transactions/', include('apps.transactions.api_urls', namespace='api_transactions')),
    # path('api/v1/mpesa/', include('apps.mpesastk.urls', namespace='api_mpesa')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
