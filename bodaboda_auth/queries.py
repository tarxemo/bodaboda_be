import graphene
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import Ride
from .outputs import UserType, ClientStatsType, RideHistoryType, ActiveRideType, RiderStatsType, EarningDataType

User = get_user_model()
PAGE_SIZE = 10


class Query(graphene.ObjectType):
    me = graphene.Field(UserType)
    client_stats = graphene.Field(ClientStatsType)
    rider_stats = graphene.Field(RiderStatsType)
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

    def resolve_rider_stats(self, info):
        user = info.context.user
        if user.is_anonymous or user.role != 'rider':
            return None
            
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        from rides.models import RideRequest
        rides = RideRequest.objects.filter(rider=user, status='completed')
        today_rides = rides.filter(completed_at__gte=today_start)
        
        today_earnings = sum(r.final_fare or r.total_fare or r.base_fare for r in today_rides)
        trips_completed = rides.count()
        
        # Calculate weekly earnings
        week_start = today_start - timedelta(days=6)
        recent_rides = rides.filter(completed_at__gte=week_start)
        
        weekly_earnings = []
        for i in range(7):
            d = week_start + timedelta(days=i)
            d_next = d + timedelta(days=1)
            day_rides = recent_rides.filter(completed_at__gte=d, completed_at__lt=d_next)
            day_amt = sum(r.final_fare or r.total_fare or r.base_fare for r in day_rides)
            day_trips = day_rides.count()
            weekly_earnings.append(EarningDataType(
                day=d.strftime('%a'),
                amount=float(day_amt),
                trips=day_trips,
                online_hours=round(day_trips * 0.5, 1) # Mock online hours based on trips
            ))
            
        target_amount = 30000.0
        target_completed_amount = min(float(today_earnings), target_amount)
            
        return RiderStatsType(
            today_earnings=float(today_earnings),
            trips_completed=trips_completed,
            online_time="8h 15m", # Mock online time
            rating=float(user.rating),
            target_amount=target_amount,
            target_completed_amount=target_completed_amount,
            weekly_earnings=weekly_earnings
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
