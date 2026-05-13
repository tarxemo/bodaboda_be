from rest_framework import serializers
from .models import Vehicle, RiderContract

class VehicleDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vehicle
        fields = [
            'logbook', 
            'insurance_doc', 
            'ownership_transfer_doc', 
            'commercial_registration_doc', 
            'local_authority_permits'
        ]

class RiderContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiderContract
        fields = ['contract_doc']
