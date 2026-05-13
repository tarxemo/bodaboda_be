import graphene
from graphene_django import DjangoObjectType
from .models import Vehicle, MaintenanceLog, FuelLog, RiderContract
from bodaboda_auth.outputs import UserType
from django.db.models import Sum
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta

class VehicleType(DjangoObjectType):
    class Meta:
        model = Vehicle
        fields = "__all__"

    today_earnings = graphene.Float()
    target_earnings = graphene.Float()
    maintenance_status = graphene.String()
    last_oil_change_km = graphene.Float()
    days_to_insurance_expiry = graphene.Int()
    days_to_inspection = graphene.Int()

    def resolve_today_earnings(self, info):
        return 0.0

    def resolve_target_earnings(self, info):
        return 30000.0

    def resolve_maintenance_status(self, info):
        if self.status == 'maintenance':
            return "Overdue"
        return "Good"
        
    def resolve_last_oil_change_km(self, info):
        log = self.maintenance_logs.filter(maintenance_type='oil_change').order_by('-performed_at').first()
        if log:
            return float(self.odometer_km - (log.odometer_at_service_km or 0))
        return 0.0
        
    def resolve_days_to_insurance_expiry(self, info):
        if self.insurance_expiry:
            delta = self.insurance_expiry - timezone.now().date()
            return max(0, delta.days)
        return 0
        
    def resolve_days_to_inspection(self, info):
        if self.inspection_due_date:
            delta = self.inspection_due_date - timezone.now().date()
            return max(0, delta.days)
        return 0


class MaintenanceLogType(DjangoObjectType):
    class Meta:
        model = MaintenanceLog
        fields = "__all__"

class FuelLogType(DjangoObjectType):
    class Meta:
        model = FuelLog
        fields = "__all__"

class RiderContractType(DjangoObjectType):
    class Meta:
        model = RiderContract
        fields = "__all__"

class OwnerStatsType(graphene.ObjectType):
    total_fleet_revenue = graphene.Float()
    active_bikes = graphene.Int()
    total_bikes = graphene.Int()
    active_riders = graphene.Int()
    avg_fleet_rating = graphene.Float()
    alerts_count = graphene.Int()
    weekly_revenue_data = graphene.List(graphene.Float)
    daily_revenue_data = graphene.List(graphene.Float)

class Query(graphene.ObjectType):
    my_fleet = graphene.List(VehicleType)
    my_riders = graphene.List(UserType)
    my_vehicle = graphene.Field(VehicleType)
    my_fuel_logs = graphene.List(FuelLogType)
    owner_stats = graphene.Field(OwnerStatsType)

    def resolve_owner_stats(self, info):
        user = info.context.user
        if not user.is_authenticated or user.role != 'owner':
            return None
            
        vehicles = Vehicle.objects.filter(owner=user)
        total_bikes = vehicles.count()
        active_bikes = vehicles.filter(status='active').count()
        
        assigned_riders = vehicles.exclude(assigned_rider__isnull=True).values_list('assigned_rider', flat=True)
        active_riders = assigned_riders.count()
        
        from rides.models import RideRequest, RideRating
        from django.db.models import Avg, Sum
        
        # Today's Revenue
        today = timezone.now().date()
        today_rides = RideRequest.objects.filter(rider_id__in=assigned_riders, status='completed', completed_at__date=today)
        total_revenue = today_rides.aggregate(Sum('final_fare'))['final_fare__sum'] or 0.0
        
        # Weekly Average Rating
        one_week_ago = timezone.now() - timedelta(days=7)
        avg_rating = RideRating.objects.filter(
            rated_user_id__in=assigned_riders, 
            created_at__gte=one_week_ago
        ).aggregate(Avg('stars'))['stars__avg'] or 0.0
        
        # Weekly Revenue Data (Last 7 days)
        weekly_revenue = []
        for i in range(6, -1, -1):
            day = timezone.now().date() - timedelta(days=i)
            day_rev = RideRequest.objects.filter(
                rider_id__in=assigned_riders, 
                status='completed', 
                completed_at__date=day
            ).aggregate(Sum('final_fare'))['final_fare__sum'] or 0.0
            weekly_revenue.append(float(day_rev))
            
        # Daily Revenue Data (Last 24 hours, grouped by 3-hour blocks for better visualization)
        daily_revenue = []
        now = timezone.now()
        for i in range(7, -1, -1):
            start_time = now - timedelta(hours=(i+1)*3)
            end_time = now - timedelta(hours=i*3)
            period_rev = RideRequest.objects.filter(
                rider_id__in=assigned_riders, 
                status='completed', 
                completed_at__gte=start_time,
                completed_at__lt=end_time
            ).aggregate(Sum('final_fare'))['final_fare__sum'] or 0.0
            daily_revenue.append(float(period_rev))
        
        return OwnerStatsType(
            total_fleet_revenue=float(total_revenue),
            active_bikes=active_bikes,
            total_bikes=total_bikes,
            active_riders=active_riders,
            avg_fleet_rating=round(float(avg_rating), 1),
            alerts_count=vehicles.filter(status='maintenance').count(),
            weekly_revenue_data=weekly_revenue,
            daily_revenue_data=daily_revenue
        )

    def resolve_my_vehicle(self, info):
        user = info.context.user
        if user.is_authenticated and user.role == 'rider':
            return Vehicle.objects.filter(assigned_rider=user).first()
        return None

    def resolve_my_fuel_logs(self, info):
        user = info.context.user
        if user.is_authenticated:
            if user.role == 'rider':
                return FuelLog.objects.filter(rider=user)
            elif user.role == 'owner':
                return FuelLog.objects.filter(vehicle__owner=user)
        return []

    def resolve_my_fleet(self, info):
        user = info.context.user
        if user.is_authenticated and user.role == 'owner':
            return Vehicle.objects.filter(owner=user)
        return Vehicle.objects.none()

    def resolve_my_riders(self, info):
        user = info.context.user
        if user.is_authenticated and user.role == 'owner':
            from bodaboda_auth.models import CustomUser
            # Find all riders assigned to the owner's vehicles
            assigned_rider_ids = Vehicle.objects.filter(owner=user).exclude(assigned_rider__isnull=True).values_list('assigned_rider_id', flat=True)
            return CustomUser.objects.filter(id__in=assigned_rider_ids)
        return []


class CreateVehicle(graphene.Mutation):
    class Arguments:
        make = graphene.String(required=True)
        model_name = graphene.String(required=True)
        year = graphene.Int(required=True)
        plate_number = graphene.String(required=True)
        fuel_type = graphene.String()
    
    success = graphene.Boolean()
    message = graphene.String()
    vehicle = graphene.Field(VehicleType)

    @classmethod
    def mutate(cls, root, info, make, model_name, year, plate_number, fuel_type="petrol"):
        user = info.context.user
        if not user.is_authenticated or user.role != 'owner':
            return CreateVehicle(success=False, message="Not authorized.")
        
        # Check if plate already exists
        if Vehicle.objects.filter(plate_number=plate_number).exists():
            return CreateVehicle(success=False, message="Vehicle with this plate number already exists.")

        try:
            vehicle = Vehicle.objects.create(
                owner=user,
                make=make,
                model_name=model_name,
                year=year,
                plate_number=plate_number,
                fuel_type=fuel_type,
                status='idle'
            )
            return CreateVehicle(success=True, message="Vehicle added successfully.", vehicle=vehicle)
        except Exception as e:
            return CreateVehicle(success=False, message=str(e))


class AssignRider(graphene.Mutation):
    class Arguments:
        vehicle_id = graphene.Int(required=True)
        rider_id = graphene.Int(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, vehicle_id, rider_id):
        user = info.context.user
        if not user.is_authenticated or user.role != 'owner':
            return AssignRider(success=False, message="Not authorized.")
            
        try:
            vehicle = Vehicle.objects.get(pk=vehicle_id, owner=user)
            from bodaboda_auth.models import CustomUser
            rider = CustomUser.objects.get(pk=rider_id, role='rider')
            
            # Check if rider is already assigned to another bike
            if Vehicle.objects.filter(assigned_rider=rider).exclude(pk=vehicle_id).exists():
                return AssignRider(success=False, message="Rider is already assigned to another vehicle.")
                
            vehicle.assigned_rider = rider
            vehicle.status = 'active'
            vehicle.save()
            return AssignRider(success=True, message=f"Rider {rider.full_name} assigned to {vehicle.plate_number}")
        except Exception as e:
            return AssignRider(success=False, message=str(e))


class UpdateVehicleDetails(graphene.Mutation):
    class Arguments:
        vehicle_id = graphene.Int(required=True)
        tin_number = graphene.String()
        engine_number = graphene.String()
        engine_capacity_cc = graphene.Int()
        is_tbs_inspected = graphene.Boolean()
        transport_group_details = graphene.String()
        chassis_number = graphene.String()
        insurance_policy_number = graphene.String()
        insurance_expiry = graphene.Date()
        logbook_control_number = graphene.String()
        insurance_sticker_number = graphene.String()
        latra_license_number = graphene.String()

    success = graphene.Boolean()
    message = graphene.String()
    vehicle = graphene.Field(VehicleType)

    def mutate(self, info, vehicle_id, **kwargs):
        user = info.context.user
        if not user.is_authenticated or user.role != 'owner':
            return UpdateVehicleDetails(success=False, message="Not authorized.")
        
        try:
            vehicle = Vehicle.objects.get(pk=vehicle_id, owner=user)
            for key, value in kwargs.items():
                setattr(vehicle, key, value)
            vehicle.save()
            return UpdateVehicleDetails(success=True, message="Vehicle details updated successfully.", vehicle=vehicle)
        except Exception as e:
            return UpdateVehicleDetails(success=False, message=str(e))

class CreateRiderContract(graphene.Mutation):
    class Arguments:
        vehicle_id = graphene.Int(required=True)
        rider_id = graphene.Int(required=True)
        expiration_date = graphene.Date(required=True)
        start_date = graphene.Date(required=True)
        # File uploads are tricky in pure graphene without specific middleware, 
        # but for now we'll define the mutation and assume the client handles the file separately if needed or we use a custom scalar.
        # However, for this task, I'll focus on the logic.

    success = graphene.Boolean()
    message = graphene.String()
    contract = graphene.Field(RiderContractType)

    def mutate(self, info, vehicle_id, rider_id, expiration_date, start_date):
        user = info.context.user
        if not user.is_authenticated or user.role != 'owner':
            return CreateRiderContract(success=False, message="Not authorized.")
        
        try:
            vehicle = Vehicle.objects.get(pk=vehicle_id, owner=user)
            from bodaboda_auth.models import CustomUser
            rider = CustomUser.objects.get(pk=rider_id, role='rider')
            
            # Deactivate old contracts for this vehicle
            RiderContract.objects.filter(vehicle=vehicle, is_active=True).update(is_active=False)
            
            contract = RiderContract.objects.create(
                vehicle=vehicle,
                owner=user,
                rider=rider,
                start_date=start_date,
                expiration_date=expiration_date,
                is_active=True
            )
            
            # Update vehicle assignment
            vehicle.assigned_rider = rider
            vehicle.status = 'active'
            vehicle.save()
            
            return CreateRiderContract(success=True, message="Contract created and rider assigned.", contract=contract)
        except Exception as e:
            return CreateRiderContract(success=False, message=str(e))

class Mutation(graphene.ObjectType):
    create_vehicle = CreateVehicle.Field()
    assign_rider = AssignRider.Field()
    update_vehicle_details = UpdateVehicleDetails.Field()
    create_rider_contract = CreateRiderContract.Field()
