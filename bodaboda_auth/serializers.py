from rest_framework import serializers
from .models import CustomUser

class KYCUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id_card_front', 'id_card_back', 'license_file', 'business_docs',
            'local_authority_letter', 'guarantor_id_front', 'guarantor_id_back'
        ]

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'full_name', 'phone', 'role', 
            'license_number', 'plate_number', 'company_name', 'tax_id',
            'nida_number', 'guarantor_name', 'guarantor_phone'
        ]
        read_only_fields = ['id', 'username', 'role']
