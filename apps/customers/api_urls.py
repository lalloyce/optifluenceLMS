"""Customer API URLs."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

app_name = 'api_customers'

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'customers', api_views.CustomerViewSet)
router.register(r'business-profiles', api_views.BusinessProfileViewSet)

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]
