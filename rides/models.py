from django.db import models
from django.conf import settings
from decimal import Decimal


class RideRequest(models.Model):
    """A booking request created by a client before a rider accepts."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_riders', 'No Riders Available'),
    ]

    VEHICLE_TYPE_CHOICES = [
        ('ride', 'Boda Ride'),
        ('delivery', 'Boda Delivery'),
    ]

    # Parties
    client = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='ride_requests'
    )
    rider = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='accepted_rides'
    )

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPE_CHOICES, default='ride')
    midway_stops = models.JSONField(null=True, blank=True, help_text="List of intermediate stops [{address, lat, lng}]")

    # Pickup Location
    pickup_address = models.CharField(max_length=512)
    pickup_lat = models.DecimalField(max_digits=10, decimal_places=7)
    pickup_lng = models.DecimalField(max_digits=10, decimal_places=7)

    # Destination
    destination_address = models.CharField(max_length=512)
    destination_lat = models.DecimalField(max_digits=10, decimal_places=7)
    destination_lng = models.DecimalField(max_digits=10, decimal_places=7)

    # Route (from Mapbox Directions API)
    route_polyline = models.TextField(blank=True, null=True, help_text="Encoded Mapbox route geometry")
    estimated_distance_km = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    estimated_duration_minutes = models.IntegerField(null=True, blank=True)

    # Fare
    base_fare = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    distance_fare = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    surge_multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('1.00'))
    total_fare = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    # Timing
    requested_at = models.DateTimeField(auto_now_add=True, db_index=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.TextField(blank=True, null=True)

    # Actual (post-ride)
    actual_distance_km = models.DecimalField(max_digits=8, decimal_places=3, null=True, blank=True)
    actual_duration_minutes = models.IntegerField(null=True, blank=True)
    final_fare = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ['-requested_at']
        verbose_name = 'Ride Request'
        verbose_name_plural = 'Ride Requests'

    def __str__(self):
        return f"Ride #{self.pk} | {self.client} → {self.destination_address} [{self.status}]"


class RideRating(models.Model):
    """Ratings given after a completed ride."""

    ride = models.OneToOneField(RideRequest, on_delete=models.CASCADE, related_name='rating')
    rated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='ratings_given'
    )
    rated_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='ratings_received'
    )
    stars = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rating {self.stars}⭐ for Ride #{self.ride_id}"


class FareRule(models.Model):
    """Dynamic fare calculation rules per vehicle type."""

    vehicle_type = models.CharField(max_length=20, unique=True)
    base_fare_tzs = models.DecimalField(max_digits=10, decimal_places=2, help_text="Flat starting fare (TZS)")
    per_km_rate_tzs = models.DecimalField(max_digits=8, decimal_places=2, help_text="Fare per kilometer (TZS)")
    per_minute_rate_tzs = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('50.00'))
    minimum_fare_tzs = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('1500.00'))
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"FareRule [{self.vehicle_type}] — Base: {self.base_fare_tzs} TZS"


class SurgeZone(models.Model):
    """Defines geographic areas where surge pricing applies."""

    name = models.CharField(max_length=255)
    center_lat = models.DecimalField(max_digits=10, decimal_places=7)
    center_lng = models.DecimalField(max_digits=10, decimal_places=7)
    radius_km = models.DecimalField(max_digits=6, decimal_places=2)
    multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('1.00'))
    is_active = models.BooleanField(default=False)
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"SurgeZone [{self.name}] x{self.multiplier}"
