from django.urls import path
from . import views
from django.views.generic import TemplateView

app_name = 'web_loans'

urlpatterns = [
    # Dashboard
    path('', views.loan_list, name='list'),
    
    # Loan Application
    path('apply/', views.loan_application, name='apply'),
    path('create/', views.loan_application, name='create'),  # Alias for apply
    path('calculator/', views.loan_calculator, name='calculator'),
    
    # Loan Management
    path('<int:pk>/', views.loan_detail, name='detail'),
    path('<int:pk>/approve/', views.loan_approve, name='approve'),
    path('<int:pk>/reject/', views.loan_reject, name='reject'),
    path('<int:pk>/disburse/', views.loan_disburse, name='disburse'),
    path('<int:pk>/schedule/', views.loan_schedule, name='schedule'),
    path('loan/<int:pk>/payment/', views.record_payment, name='record_payment'),
    
    # Application Management
    path('application/<int:pk>/', views.application_detail, name='application_detail'),
    path('api/customers/<int:pk>/details/', views.customer_details_api, name='customer_details_api'),
    path('api/guarantors/', views.guarantor_list_api, name='guarantor_list_api'),

    
    # Loan Product Management
    path('loan-products/', views.loan_product_list, name='loan_product_list'),
]
