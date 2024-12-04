"""Customer serializers."""
from rest_framework import serializers
from .models import Customer, BusinessProfile, CustomerDocument

class BusinessProfileSerializer(serializers.ModelSerializer):
    """Serializer for business profile."""
    
    class Meta:
        model = BusinessProfile
        exclude = ('customer',)

class CustomerDocumentSerializer(serializers.ModelSerializer):
    """Serializer for customer documents."""
    
    class Meta:
        model = CustomerDocument
        exclude = ('customer',)

class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for customer model."""
    business_profile = BusinessProfileSerializer(required=False)
    documents = CustomerDocumentSerializer(many=True, read_only=True)
    profile_completion = serializers.FloatField(read_only=True)
    
    class Meta:
        model = Customer
        fields = '__all__'
        read_only_fields = (
            'verification_status', 'verified_by', 'verified_at',
            'recommendation_score', 'last_recommendation_date',
            'recommended_products', 'created_by', 'created_at',
            'updated_at'
        )
    
    def create(self, validated_data):
        """Create customer with nested business profile."""
        business_profile_data = validated_data.pop('business_profile', None)
        customer = Customer.objects.create(**validated_data)
        
        if business_profile_data and customer.is_business:
            BusinessProfile.objects.create(
                customer=customer,
                **business_profile_data
            )
        
        return customer
    
    def update(self, instance, validated_data):
        """Update customer with nested business profile."""
        business_profile_data = validated_data.pop('business_profile', None)
        
        # Update customer fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update or create business profile
        if business_profile_data and instance.is_business:
            BusinessProfile.objects.update_or_create(
                customer=instance,
                defaults=business_profile_data
            )
        elif not instance.is_business:
            BusinessProfile.objects.filter(customer=instance).delete()
        
        return instance

class CustomerListSerializer(serializers.ModelSerializer):
    """Simplified serializer for customer list view."""
    
    class Meta:
        model = Customer
        fields = (
            'id', 'first_name', 'last_name', 'email',
            'phone_number', 'customer_type', 'verification_status',
            'created_at'
        )
