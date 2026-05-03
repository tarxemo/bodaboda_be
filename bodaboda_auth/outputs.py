import graphene
from graphene_django import DjangoObjectType
from .models import CustomUser, Ride


class UserType(DjangoObjectType):
    class Meta:
        model = CustomUser
        fields = (
            "id", "username", "email", "full_name", "phone", "role",
            "license_number", "plate_number", "company_name", "tax_id",
            "rating", "total_trips",
        )


class RideType(DjangoObjectType):
    class Meta:
        model = Ride
        fields = (
            "id", "pickup", "destination", "status", "amount",
            "distance", "duration", "payment_method", "created_at",
            "completed_at", "estimated_arrival", "rider", "client",
            "pickup_lat", "pickup_lng", "dest_lat", "dest_lng",
        )

    # Format date for frontend
    date = graphene.String()
    formatted_duration = graphene.String()
    formatted_distance = graphene.String()
    formatted_amount = graphene.String()

    def resolve_date(self, info):
        return self.created_at.strftime('%Y-%m-%d')

    def resolve_formatted_duration(self, info):
        if self.duration:
            return f"{self.duration} mins"
        return '--'

    def resolve_formatted_distance(self, info):
        if self.distance:
            return f"{self.distance:.1f} km"
        return '--'

    def resolve_formatted_amount(self, info):
        return f"{int(self.amount):,}"


class ActiveRideType(graphene.ObjectType):
    id = graphene.ID()
    pickup = graphene.String()
    destination = graphene.String()
    status = graphene.String()
    estimated_arrival = graphene.String()
    rider = graphene.Field(UserType)


class ClientStatsType(graphene.ObjectType):
    total_rides = graphene.Int()
    total_spent = graphene.Float()
    loyalty_points = graphene.Int()
    carbon_saved = graphene.Float()
    active_ride = graphene.Field(ActiveRideType)


class RideHistoryType(graphene.ObjectType):
    total = graphene.Int()
    rides = graphene.List(RideType)


class AuthResponse(graphene.ObjectType):
    success = graphene.Boolean()
    message = graphene.String()
    user = graphene.Field(UserType)
