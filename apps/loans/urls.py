from django.urls import path
from . import views
from .views import risk_dashboard, repayment, loan_detail

app_name = 'loans'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Loan Application
    path('create/', views.loan_create, name='loans.create'),
    path('apply/', views.loan_application, name='loans.apply'),
    path('calculator/', views.loan_calculator, name='loans.calculator'),
    
    # Loan Management
    path('list/', views.loan_list, name='loans.list'),
    path('<int:pk>/', loan_detail.LoanDetailView.as_view(), name='loan_detail'),
    path('<int:pk>/edit/', views.loan_edit, name='loans.edit'),
    path('<int:pk>/delete/', views.loan_delete, name='loans.delete'),
    path('<int:pk>/approve/', views.loan_approve, name='loans.approve'),
    path('<int:pk>/reject/', views.loan_reject, name='loans.reject'),
    path('<int:pk>/disburse/', views.loan_disburse, name='loans.disburse'),
    
    # Document Management
    path('<int:pk>/documents/', views.loan_documents, name='loans.documents'),
    path('<int:pk>/documents/<int:doc_pk>/delete/', views.loan_document_delete, name='loans.document_delete'),
    path('<int:pk>/schedule/', views.loan_schedule, name='loans.schedule'),
    
    # Repayment URLs
    path(
        '<int:loan_id>/repayment/create/',
        repayment.RepaymentCreateView.as_view(),
        name='repayment_create'
    ),
    path(
        '<int:loan_id>/repayment/schedule/',
        repayment.RepaymentScheduleView.as_view(),
        name='repayment_schedule'
    ),
    path(
        '<int:loan_id>/repayment/transactions/',
        repayment.TransactionListView.as_view(),
        name='repayment_transactions'
    ),
    path(
        'schedule/<int:schedule_id>/waive-penalty/',
        repayment.WaivePenaltyView.as_view(),
        name='waive_penalty'
    ),
    path(
        '<int:loan_id>/balance/',
        repayment.get_loan_balance,
        name='get_loan_balance'
    ),
    
    # Risk Dashboard URLs
    path(
        'risk-dashboard/',
        risk_dashboard.RiskDashboardView.as_view(),
        name='risk_dashboard'
    ),
    path(
        'risk-dashboard/data/',
        risk_dashboard.RiskDashboardDataView.as_view(),
        name='risk_dashboard_data'
    ),
]
