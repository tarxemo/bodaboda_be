from rest_framework import serializers
from .models import CustomUser

class KYCUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id_card_front', 'id_card_back', 'license_file', 'business_docs']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'full_name', 'phone', 'role', 
                  'license_number', 'plate_number', 'company_name', 'tax_id']
        read_only_fields = ['id', 'username', 'role']
