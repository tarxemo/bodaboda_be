import graphene
from graphene_django import DjangoObjectType
from .models import RideRequest, RideRating, FareRule
from django.shortcuts import get_object_or_404
from decimal import Decimal
import math

class RideRequestType(DjangoObjectType):
    class Meta:
        model = RideRequest
        fields = "__all__"

class RideRatingType(DjangoObjectType):
    class Meta:
        model = RideRating
        fields = "__all__"

class RideEstimateType(graphene.ObjectType):
    estimated_distance_km = graphene.Float()
    estimated_fare_tzs = graphene.Float()

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat/2) * math.sin(dLat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dLon/2) * math.sin(dLon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

class Query(graphene.ObjectType):
    my_rides = graphene.List(RideRequestType)
    ride_detail = graphene.Field(RideRequestType, id=graphene.Int(required=True))

    def resolve_my_rides(self, info):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required")
        return RideRequest.objects.filter(client=user).order_by('-requested_at')

    def resolve_ride_detail(self, info, id):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required")
        return get_object_or_404(RideRequest, pk=id, client=user)

class EstimateRideMutation(graphene.Mutation):
    class Arguments:
        pickup_lat = graphene.Float(required=True)
        pickup_lng = graphene.Float(required=True)
        destination_lat = graphene.Float(required=True)
        destination_lng = graphene.Float(required=True)
        ride_type = graphene.String(default_value='ride')
        midway_stops = graphene.String(required=False)

    estimate = graphene.Field(RideEstimateType)

    def mutate(self, info, pickup_lat, pickup_lng, destination_lat, destination_lng, ride_type, midway_stops=None):
        import json
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required")
            
        total_dist = 0
        points = [(pickup_lat, pickup_lng)]
        
        if midway_stops:
            try:
                stops = json.loads(midway_stops)
                for s in stops:
                    points.append((s['lat'], s['lng']))
            except:
                pass
                
        points.append((destination_lat, destination_lng))
        
        for i in range(len(points)-1):
            total_dist += calculate_distance(points[i][0], points[i][1], points[i+1][0], points[i+1][1])
        
        rule = FareRule.objects.filter(ride_type=ride_type).first()
        if not rule:
            base_fare = Decimal('1500') # Updated default
            per_km_rate = Decimal('700')
        else:
            base_fare = rule.base_fare_tzs
            per_km_rate = rule.per_km_rate_tzs
        
        estimated_fare = base_fare + (Decimal(str(total_dist)) * per_km_rate)
        
        return EstimateRideMutation(estimate=RideEstimateType(
            estimated_distance_km=round(total_dist, 2),
            estimated_fare_tzs=round(estimated_fare, 2)
        ))

class RequestRideMutation(graphene.Mutation):
    class Arguments:
        pickup_address = graphene.String(required=True)
        pickup_lat = graphene.Float(required=True)
        pickup_lng = graphene.Float(required=True)
        destination_address = graphene.String(required=True)
        destination_lat = graphene.Float(required=True)
        destination_lng = graphene.Float(required=True)
        ride_type = graphene.String(default_value='ride')
        midway_stops = graphene.String(required=False)

    ride = graphene.Field(RideRequestType)

    def mutate(self, info, pickup_address, pickup_lat, pickup_lng, destination_address, destination_lat, destination_lng, ride_type, midway_stops=None):
        import json
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required")
            
        rule = FareRule.objects.filter(ride_type=ride_type).first()
        base_fare = rule.base_fare_tzs if rule else Decimal('1500.00')
        per_km_rate = rule.per_km_rate_tzs if rule else Decimal('700.00')
        
        stops_data = None
        points = [(pickup_lat, pickup_lng)]
        if midway_stops:
            try:
                stops_data = json.loads(midway_stops)
                for s in stops_data:
                    points.append((s['lat'], s['lng']))
            except:
                pass
        
        points.append((destination_lat, destination_lng))
        
        total_dist = 0
        for i in range(len(points)-1):
            total_dist += calculate_distance(points[i][0], points[i][1], points[i+1][0], points[i+1][1])
            
        distance_fare = Decimal(str(total_dist)) * per_km_rate
        total_fare = base_fare + distance_fare

        ride = RideRequest.objects.create(
            client=user,
            pickup_address=pickup_address,
            pickup_lat=pickup_lat,
            pickup_lng=pickup_lng,
            destination_address=destination_address,
            destination_lat=destination_lat,
            destination_lng=destination_lng,
            ride_type=ride_type,
            base_fare=base_fare,
            distance_fare=distance_fare,
            total_fare=total_fare,
            midway_stops=stops_data
        )
        return RequestRideMutation(ride=ride)

class RateRideMutation(graphene.Mutation):
    class Arguments:
        ride_id = graphene.Int(required=True)
        stars = graphene.Int(required=True)
        comment = graphene.String(required=False)

    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, ride_id, stars, comment=""):
        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required")
            
        ride = get_object_or_404(RideRequest, pk=ride_id, client=user)
        if ride.status != 'completed':
            return RateRideMutation(success=False, message="Can only rate completed rides.")
        if hasattr(ride, 'rating'):
            return RateRideMutation(success=False, message="Ride already rated.")
            
        RideRating.objects.create(
            ride=ride,
            rated_by=user,
            rated_user=ride.rider,
            stars=stars,
            comment=comment
        )
        return RateRideMutation(success=True, message="Rating submitted.")

class Mutation(graphene.ObjectType):
    estimate_ride = EstimateRideMutation.Field()
    request_ride = RequestRideMutation.Field()
    rate_ride = RateRideMutation.Field()
