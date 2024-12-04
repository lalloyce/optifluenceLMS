from django.urls import path
from . import views

app_name = 'web_customers'

urlpatterns = [
    path('', views.customer_list, name='customers.list'),
    path('create/', views.customer_create, name='customers.create'),
    path('<int:pk>/', views.customer_detail, name='customers.detail'),
    path('<int:pk>/edit/', views.customer_edit, name='customers.edit'),
    path('<int:pk>/delete/', views.customer_delete, name='customers.delete'),
]
