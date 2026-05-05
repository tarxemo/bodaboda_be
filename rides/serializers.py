from rest_framework import serializers
from .models import RideRequest, RideRating, FareRule

class RideRequestSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.full_name', read_only=True)
    rider_name = serializers.CharField(source='rider.full_name', read_only=True)
    
    class Meta:
        model = RideRequest
        fields = '__all__'
        read_only_fields = ['client', 'status', 'total_fare', 'requested_at', 'accepted_at', 'started_at', 'completed_at', 'cancelled_at']

class RideEstimateSerializer(serializers.Serializer):
    pickup_lat = serializers.DecimalField(max_digits=10, decimal_places=7)
    pickup_lng = serializers.DecimalField(max_digits=10, decimal_places=7)
    destination_lat = serializers.DecimalField(max_digits=10, decimal_places=7)
    destination_lng = serializers.DecimalField(max_digits=10, decimal_places=7)
    vehicle_type = serializers.ChoiceField(choices=RideRequest.VEHICLE_TYPE_CHOICES, default='economy')

class RideRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = RideRating
        fields = ['stars', 'comment']
