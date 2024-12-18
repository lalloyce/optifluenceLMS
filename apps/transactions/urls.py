from django.urls import path
from . import views

app_name = 'web_transactions'

urlpatterns = [
    path('', views.TransactionListView.as_view(), name='list'),
    path('create/', views.TransactionCreateView.as_view(), name='create'),
    path('<int:pk>/', views.TransactionDetailView.as_view(), name='detail'),
    path('<int:pk>/reverse/', views.TransactionReverseView.as_view(), name='reverse'),
    path('ajax/load-loans/', views.load_loans, name='load_loans'),
]
