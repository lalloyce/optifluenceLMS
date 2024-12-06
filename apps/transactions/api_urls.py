from django.urls import path
from . import api_views

app_name = 'api_transactions'

urlpatterns = [
    path('', api_views.TransactionListAPIView.as_view(), name='list'),
    path('create/', api_views.TransactionCreateAPIView.as_view(), name='create'),
    path('<int:pk>/', api_views.TransactionDetailAPIView.as_view(), name='detail'),
    path('<int:pk>/reverse/', api_views.TransactionReverseAPIView.as_view(), name='reverse'),
]
