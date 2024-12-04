"""Customer API views."""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from .models import Customer, BusinessProfile
from .serializers import (
    CustomerSerializer, CustomerListSerializer,
    BusinessProfileSerializer
)
from .services import CustomerService

class CustomerViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing customers.
    """
    permission_classes = [IsAuthenticated]
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['customer_type', 'verification_status', 'is_active']
    search_fields = ['first_name', 'last_name', 'email', 'phone_number']
    ordering_fields = ['created_at', 'updated_at', 'recommendation_score']
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'list':
            return CustomerListSerializer
        return CustomerSerializer
    
    def perform_create(self, serializer):
        """Set created_by when creating a customer."""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """Verify a customer."""
        customer = self.get_object()
        notes = request.data.get('notes', '')
        
        try:
            CustomerService.verify_customer(
                customer=customer,
                verified_by=request.user,
                notes=notes
            )
            return Response({'status': 'customer verified'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def update_recommendations(self, request, pk=None):
        """Update customer recommendations."""
        customer = self.get_object()
        
        try:
            CustomerService.update_customer_recommendations(customer)
            return Response({'status': 'recommendations updated'})
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['get'])
    def insights(self, request, pk=None):
        """Get customer insights."""
        customer = self.get_object()
        insights = CustomerService.get_customer_insights(customer)
        return Response(insights)
    
    @action(detail=False, methods=['get'])
    def pending_verification(self, request):
        """List customers pending verification."""
        customers = CustomerService.get_customers_requiring_verification()
        page = self.paginate_queryset(customers)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(customers, many=True)
        return Response(serializer.data)

class BusinessProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing business profiles.
    """
    permission_classes = [IsAuthenticated]
    queryset = BusinessProfile.objects.all()
    serializer_class = BusinessProfileSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['business_type']
    search_fields = ['business_name', 'registration_number', 'tax_id']
    
    def perform_create(self, serializer):
        """Ensure business profile is linked to a business customer."""
        customer_id = self.request.data.get('customer')
        if not customer_id:
            return Response(
                {'error': 'customer ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            customer = Customer.objects.get(id=customer_id)
            if not customer.is_business:
                return Response(
                    {'error': 'customer must be a business type'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer.save(customer=customer)
        except Customer.DoesNotExist:
            return Response(
                {'error': 'customer not found'},
                status=status.HTTP_404_NOT_FOUND
            )
