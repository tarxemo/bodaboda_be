import graphene
from django.contrib.auth import get_user_model
from .models import Ride
from .outputs import UserType, ClientStatsType, RideHistoryType, ActiveRideType

User = get_user_model()
PAGE_SIZE = 10


class Query(graphene.ObjectType):
    me = graphene.Field(UserType)
    client_stats = graphene.Field(ClientStatsType)
    ride_history = graphene.Field(
        RideHistoryType,
        page=graphene.Int(default_value=1),
        page_size=graphene.Int(default_value=PAGE_SIZE),
    )
    check_email = graphene.Boolean(email=graphene.String(required=True))

    def resolve_me(self, info):
        user = info.context.user
        if user.is_anonymous:
            return None
        return user

    def resolve_client_stats(self, info):
        user = info.context.user
        if user.is_anonymous:
            return None

        rides = Ride.objects.filter(client=user)
        completed = rides.filter(status='completed')
        active = rides.filter(status='in_progress').first()

        total_spent = float(sum(r.amount for r in completed))
        total_rides = completed.count()
        # 100 points per ride, +50 for 10+ rides
        loyalty = total_rides * 100 + (50 if total_rides >= 10 else 0)
        # Rough CO2 saved vs car: 0.12 kg/km for boda vs 0.21 kg/km for car
        total_km = sum((r.distance or 0) for r in completed)
        carbon_saved = round(total_km * 0.09, 1)

        active_ride = None
        if active:
            arrival_str = (
                active.estimated_arrival.strftime('%H:%M')
                if active.estimated_arrival else None
            )
            active_ride = ActiveRideType(
                id=active.id,
                pickup=active.pickup,
                destination=active.destination,
                status=active.status,
                estimated_arrival=arrival_str,
                rider=active.rider,
            )

        return ClientStatsType(
            total_rides=total_rides,
            total_spent=total_spent,
            loyalty_points=loyalty,
            carbon_saved=carbon_saved,
            active_ride=active_ride,
        )

    def resolve_ride_history(self, info, page=1, page_size=PAGE_SIZE):
        user = info.context.user
        if user.is_anonymous:
            return RideHistoryType(total=0, rides=[])

        qs = Ride.objects.filter(client=user).select_related('rider')
        total = qs.count()
        offset = (page - 1) * page_size
        rides = qs[offset: offset + page_size]
        return RideHistoryType(total=total, rides=list(rides))

    def resolve_check_email(self, info, email):
        return User.objects.filter(email=email).exists()
