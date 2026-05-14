from django.contrib import admin
from .models import RideRequest, RideRating, FareRule, SurgeZone


@admin.register(RideRequest)
class RideRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'rider', 'pickup_address', 'destination_address', 'status', 'total_fare', 'requested_at')
    list_filter = ('status', 'ride_type', 'requested_at')
    search_fields = ('client__username', 'rider__username', 'pickup_address', 'destination_address')
    readonly_fields = ('requested_at', 'accepted_at', 'started_at', 'completed_at', 'cancelled_at')
    date_hierarchy = 'requested_at'


@admin.register(RideRating)
class RideRatingAdmin(admin.ModelAdmin):
    list_display = ('ride', 'rated_by', 'rated_user', 'stars', 'created_at')
    list_filter = ('stars',)


@admin.register(FareRule)
class FareRuleAdmin(admin.ModelAdmin):
    list_display = ('ride_type', 'base_fare_tzs', 'per_km_rate_tzs', 'minimum_fare_tzs', 'is_active', 'updated_at')
    list_editable = ('is_active',)


@admin.register(SurgeZone)
class SurgeZoneAdmin(admin.ModelAdmin):
    list_display = ('name', 'multiplier', 'is_active', 'starts_at', 'ends_at')
    list_editable = ('is_active', 'multiplier')
