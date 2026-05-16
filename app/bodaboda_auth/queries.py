import graphene
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import Ride
from .outputs import UserType, ClientStatsType, RideHistoryType, ActiveRideType, RiderStatsType, EarningDataType, BossReportType, SubmissionSummaryType

User = get_user_model()
PAGE_SIZE = 10


class Query(graphene.ObjectType):
    me = graphene.Field(UserType)
    client_stats = graphene.Field(ClientStatsType)
    rider_stats = graphene.Field(RiderStatsType)
    boss_report = graphene.Field(BossReportType)
    ride_history = graphene.Field(
        RideHistoryType,
        page=graphene.Int(default_value=1),
        page_size=graphene.Int(default_value=PAGE_SIZE),
    )
    check_email = graphene.Boolean(email=graphene.String(required=True))
    all_riders = graphene.List(UserType)

    def resolve_all_riders(self, info):
        return User.objects.filter(role__in=['rider', 'employed_rider'])

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
        if user.is_anonymous or user.role not in ('rider', 'employed_rider'):
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
        
        weekly_total = sum(d.amount for d in weekly_earnings)
        avg_earning = 0.0
        if trips_completed > 0:
            avg_earning = float(sum(r.final_fare or r.total_fare or r.base_fare for r in rides)) / trips_completed
            
        from fleet.models import Vehicle
        assigned_v = Vehicle.objects.filter(assigned_rider=user).first()
        plate = assigned_v.plate_number if assigned_v else "N/A"
            
        # Active ride
        active_ride = RideRequest.objects.filter(
            rider=user, 
            status__in=['accepted', 'confirmed', 'in_progress']
        ).first()
        
        # Pending requests (all of them for now, sorting can be added later)
        pending_requests = RideRequest.objects.filter(status='pending')
            
        return RiderStatsType(
            today_earnings=float(today_earnings),
            trips_completed=trips_completed,
            online_time="8h 15m", # Still mock as we don't have session tracking yet
            rating=float(user.rating),
            target_amount=target_amount,
            target_completed_amount=target_completed_amount,
            weekly_earnings=weekly_earnings,
            weekly_total=float(weekly_total),
            avg_earning_per_ride=float(avg_earning),
            active_vehicle_plate=plate,
            active_ride=active_ride,
            pending_requests=pending_requests
        )

    def resolve_ride_history(self, info, page=1, page_size=PAGE_SIZE):
        user = info.context.user
        if user.is_anonymous:
            return RideHistoryType(total=0, rides=[])

        from rides.models import RideRequest
        if user.role in ('rider', 'employed_rider'):
            qs = RideRequest.objects.filter(rider=user)
        else:
            qs = RideRequest.objects.filter(client=user)
            
        total = qs.count()
        offset = (page - 1) * page_size
        rides_db = qs.order_by('-requested_at')[offset: offset + page_size]
        
        # Map RideRequest fields to the output type
        rides_output = []
        for r in rides_db:
            rides_output.append({
                "id": r.id,
                "pickup": r.pickup_address,
                "destination": r.destination_address,
                "date": r.requested_at,
                "amount": float(r.final_fare or r.total_fare or 0),
                "status": r.status,
                "distance": float(r.actual_distance_km or r.estimated_distance_km or 0),
                "duration": r.actual_duration_minutes or r.estimated_duration_minutes or 0,
                "paymentMethod": "cash", # Default for now
                "rider": r.rider
            })
            
        return RideHistoryType(total=total, rides=rides_output)

    def resolve_check_email(self, info, email):
        return User.objects.filter(email=email).exists()

    def resolve_boss_report(self, info):
        user = info.context.user
        if user.is_anonymous or user.role != 'employed_rider':
            return None

        boss = user.registered_by
        if not boss:
            return None

        from django.utils import timezone
        from datetime import timedelta
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        from rides.models import RideRequest
        today_rides = RideRequest.objects.filter(
            rider=user, status='completed', completed_at__gte=today_start
        )
        today_gross = float(sum(r.final_fare or r.total_fare or r.base_fare for r in today_rides))

        # Get today's submissions to boss
        try:
            from fleet.models import DailyFeeSubmission
            today_subs = DailyFeeSubmission.objects.filter(
                rider=user, submission_date=today_start.date()
            )
            today_submitted = float(sum(s.amount_tzs for s in today_subs))

            # Weekly history
            week_start = today_start - timedelta(days=6)
            weekly_subs = DailyFeeSubmission.objects.filter(
                rider=user, submission_date__gte=week_start.date()
            ).order_by('-submission_date')
            weekly_submitted = float(sum(s.amount_tzs for s in weekly_subs))

            # Consistency: days with at least one submission in last 30 days
            thirty_start = today_start - timedelta(days=29)
            month_subs = DailyFeeSubmission.objects.filter(
                rider=user, submission_date__gte=thirty_start.date()
            )
            days_with_submission = month_subs.values('submission_date').distinct().count()
            consistency = min(100, round((days_with_submission / 30) * 100))

            history = [
                SubmissionSummaryType(
                    date=str(s.submission_date),
                    amount_tzs=float(s.amount_tzs),
                    status=s.status
                )
                for s in weekly_subs[:14]
            ]
        except Exception:
            today_submitted = 0.0
            weekly_submitted = 0.0
            consistency = 0
            history = []

        daily_target = float(user.daily_target_tzs or 0)
        remaining = max(0, daily_target - today_submitted)
        net_profit = max(0, today_gross - daily_target)

        return BossReportType(
            boss_name=boss.full_name,
            boss_phone=boss.phone,
            boss_company=boss.company_name or 'N/A',
            daily_target_tzs=daily_target,
            today_gross_earnings=today_gross,
            today_submitted_tzs=today_submitted,
            today_remaining_to_pay=remaining,
            today_net_profit=net_profit,
            weekly_submitted=weekly_submitted,
            consistency_percent=consistency,
            submission_history=history
        )
