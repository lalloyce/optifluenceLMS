from django.urls import path
from . import api_views

app_name = 'api_loans'

urlpatterns = [
    path('', api_views.LoanListAPIView.as_view(), name='list'),
    path('create/', api_views.LoanCreateAPIView.as_view(), name='create'),
    path('<int:pk>/', api_views.LoanDetailAPIView.as_view(), name='detail'),
    path('<int:pk>/approve/', api_views.LoanApproveAPIView.as_view(), name='approve'),
    path('<int:pk>/reject/', api_views.LoanRejectAPIView.as_view(), name='reject'),
    path('<int:pk>/disburse/', api_views.LoanDisburseAPIView.as_view(), name='disburse'),
    path('<int:pk>/schedule/', api_views.LoanScheduleAPIView.as_view(), name='schedule'),
]
