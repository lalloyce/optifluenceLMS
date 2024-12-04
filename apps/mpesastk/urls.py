"""MPesa STK Push URLs."""
from django.urls import path
from . import views

app_name = 'mpesastk'

urlpatterns = [
    path('', views.STKTransactionListView.as_view(), name='transactions'),
    path('pay/', views.STKPushView.as_view(), name='stk_push'),
    path('api/stk-push/', views.STKPushAPIView.as_view(), name='stk_push_api'),
    path('api/callback/', views.STKCallbackView.as_view(), name='callback'),
    path('api/query/', views.STKQueryView.as_view(), name='query'),
]
