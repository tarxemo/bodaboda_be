from django.db import models
from django.conf import settings


class LiveLocation(models.Model):
    """Real-time GPS location broadcast by riders."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='live_location'
    )
    lat = models.DecimalField(max_digits=10, decimal_places=7)
    lng = models.DecimalField(max_digits=10, decimal_places=7)
    heading = models.FloatField(default=0.0, help_text="Degrees from North (0-360)")
    speed_kmh = models.FloatField(default=0.0)
    accuracy_meters = models.FloatField(default=0.0)
    is_online = models.BooleanField(default=False, db_index=True)
    last_updated = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        verbose_name = "Live Location"
        verbose_name_plural = "Live Locations"

    def __str__(self):
        return f"{self.user} @ ({self.lat}, {self.lng}) | Online: {self.is_online}"


class LocationHistory(models.Model):
    """Historical GPS breadcrumb trail recorded during a ride."""

    ride = models.ForeignKey(
        'rides.RideRequest', on_delete=models.CASCADE, related_name='location_history'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='location_history'
    )
    lat = models.DecimalField(max_digits=10, decimal_places=7)
    lng = models.DecimalField(max_digits=10, decimal_places=7)
    heading = models.FloatField(default=0.0)
    speed_kmh = models.FloatField(default=0.0)
    recorded_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['recorded_at']
        verbose_name = "Location Breadcrumb"

    def __str__(self):
        return f"Breadcrumb Ride#{self.ride_id} @ {self.recorded_at.strftime('%H:%M:%S')}"


class MapRoute(models.Model):
    """Stores a Mapbox route calculation result for a ride."""

    ride = models.OneToOneField(
        'rides.RideRequest', on_delete=models.CASCADE, related_name='map_route'
    )
    # Mapbox encoded polyline geometry
    route_geometry = models.TextField(help_text="Mapbox encoded route geometry string")
    distance_meters = models.IntegerField()
    duration_seconds = models.IntegerField()
    # Raw Mapbox API response stored for debugging/re-use
    raw_response = models.JSONField(null=True, blank=True)
    calculated_at = models.DateTimeField(auto_now_add=True)

    def distance_km(self):
        return round(self.distance_meters / 1000, 2)

    def duration_minutes(self):
        return round(self.duration_seconds / 60, 1)

    def __str__(self):
        return f"Route for Ride#{self.ride_id} — {self.distance_km()} km"


class Geofence(models.Model):
    """Define geographic zones (e.g., no-go zones, service areas, surge zones)."""

    ZONE_TYPE_CHOICES = [
        ('service_area', 'Service Area'),
        ('no_go', 'No-Go Zone'),
        ('hotspot', 'Pickup Hotspot'),
        ('surge', 'Surge Pricing Zone'),
    ]

    name = models.CharField(max_length=255)
    zone_type = models.CharField(max_length=20, choices=ZONE_TYPE_CHOICES)
    # GeoJSON polygon or circle definition stored as JSON
    boundary = models.JSONField(help_text="GeoJSON polygon coordinates")
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Geofence [{self.zone_type}]: {self.name}"
