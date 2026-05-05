from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import RideRequest, RideRating, FareRule
from .serializers import RideRequestSerializer, RideEstimateSerializer, RideRatingSerializer
from decimal import Decimal
import math

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat/2) * math.sin(dLat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dLon/2) * math.sin(dLon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

class RideEstimateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = RideEstimateSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            dist_km = calculate_distance(float(data['pickup_lat']), float(data['pickup_lng']), float(data['destination_lat']), float(data['destination_lng']))
            
            rule = FareRule.objects.filter(vehicle_type=data.get('vehicle_type', 'economy')).first()
            if not rule:
                base_fare = Decimal('1000')
                per_km_rate = Decimal('500')
            else:
                base_fare = rule.base_fare_tzs
                per_km_rate = rule.per_km_rate_tzs
            
            estimated_fare = base_fare + (Decimal(str(dist_km)) * per_km_rate)
            return Response({
                'estimated_distance_km': round(dist_km, 2),
                'estimated_fare_tzs': round(estimated_fare, 2)
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RideRequestListCreateView(generics.ListCreateAPIView):
    serializer_class = RideRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return RideRequest.objects.filter(client=self.request.user).order_by('-requested_at')

    def perform_create(self, serializer):
        vehicle_type = self.request.data.get('vehicle_type', 'economy')
        rule = FareRule.objects.filter(vehicle_type=vehicle_type).first()
        base_fare = rule.base_fare_tzs if rule else Decimal('1000.00')
        serializer.save(client=self.request.user, base_fare=base_fare)

class RideDetailView(generics.RetrieveAPIView):
    serializer_class = RideRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return RideRequest.objects.filter(client=self.request.user)

class RideRateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        ride = get_object_or_404(RideRequest, pk=pk, client=request.user)
        if ride.status != 'completed':
            return Response({"detail": "Can only rate completed rides."}, status=status.HTTP_400_BAD_REQUEST)
        if hasattr(ride, 'rating'):
            return Response({"detail": "Ride already rated."}, status=status.HTTP_400_BAD_REQUEST)
            
        serializer = RideRatingSerializer(data=request.data)
        if serializer.is_valid():
            RideRating.objects.create(
                ride=ride,
                rated_by=request.user,
                rated_user=ride.rider,
                stars=serializer.validated_data['stars'],
                comment=serializer.validated_data.get('comment', '')
            )
            return Response({"detail": "Rating submitted."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
