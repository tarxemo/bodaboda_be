import graphene
from graphene_django import DjangoObjectType
from .models import CustomUser, Ride
from rides.models import RideRequest


class UserType(DjangoObjectType):
    class Meta:
        model = CustomUser
        fields = (
            "id", "username", "email", "full_name", "phone", "role",
            "license_number", "plate_number", "company_name", "tax_id",
            "rating", "total_trips", "nida_number", "guarantor_name", "guarantor_phone",
            "is_suspended", "id_card_front", "id_card_back", "license_file", 
            "local_authority_letter", "guarantor_id_front", "guarantor_id_back",
            "daily_target_tzs", "registered_by"
        )
    
    kyc_status = graphene.String()
    is_fully_registered = graphene.Boolean()
    
    def resolve_kyc_status(self, info):
        # Logic to determine KYC status based on uploaded files
        required_files = [
            self.id_card_front, self.id_card_back, self.license_file, 
            self.local_authority_letter, self.guarantor_id_front
        ]
        uploaded_count = sum(1 for f in required_files if f)
        
        if uploaded_count == len(required_files):
            return "verified"
        if uploaded_count > 0:
            return "pending"
        return "not_started"

    def resolve_is_fully_registered(self, info):
        required_fields = [
            self.id_card_front, self.id_card_back, self.license_file,
            self.nida_number, self.local_authority_letter,
            self.guarantor_name, self.guarantor_phone,
            self.guarantor_id_front, self.guarantor_id_back
        ]
        return all(required_fields)


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


class RideRequestType(DjangoObjectType):
    class Meta:
        model = RideRequest
        fields = (
            "id", "pickup_address", "destination_address", "pickup_lat",
            "pickup_lng", "destination_lat", "destination_lng", "status",
            "total_fare", "client", "rider", "requested_at"
        )

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


class EarningDataType(graphene.ObjectType):
    day = graphene.String()
    amount = graphene.Float()
    trips = graphene.Int()
    online_hours = graphene.Float()


class RiderStatsType(graphene.ObjectType):
    today_earnings = graphene.Float()
    trips_completed = graphene.Int()
    online_time = graphene.String()
    rating = graphene.Float()
    target_amount = graphene.Float()
    target_completed_amount = graphene.Float()
    weekly_earnings = graphene.List(EarningDataType)
    weekly_total = graphene.Float()
    avg_earning_per_ride = graphene.Float()
    active_vehicle_plate = graphene.String()
    active_ride = graphene.Field(RideRequestType)
    pending_requests = graphene.List(RideRequestType)


class RideHistoryType(graphene.ObjectType):
    total = graphene.Int()
    rides = graphene.List(RideType)


class AuthResponse(graphene.ObjectType):
    success = graphene.Boolean()
    message = graphene.String()
    user = graphene.Field(UserType)


class BossReportType(graphene.ObjectType):
    """Data for the employed rider's Boss Report page."""
    boss_name = graphene.String()
    boss_phone = graphene.String()
    boss_company = graphene.String()
    daily_target_tzs = graphene.Float()
    today_gross_earnings = graphene.Float()
    today_submitted_tzs = graphene.Float()
    today_remaining_to_pay = graphene.Float()
    today_net_profit = graphene.Float()
    weekly_submitted = graphene.Float()
    consistency_percent = graphene.Int()
    submission_history = graphene.List('bodaboda_auth.outputs.SubmissionSummaryType')


class SubmissionSummaryType(graphene.ObjectType):
    date = graphene.String()
    amount_tzs = graphene.Float()
    status = graphene.String()
