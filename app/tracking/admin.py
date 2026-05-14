from django.contrib import admin
from .models import LiveLocation, LocationHistory, MapRoute, Geofence


@admin.register(LiveLocation)
class LiveLocationAdmin(admin.ModelAdmin):
    list_display = ('user', 'lat', 'lng', 'speed_kmh', 'is_online', 'last_updated')
    list_filter = ('is_online',)
    search_fields = ('user__username',)


@admin.register(LocationHistory)
class LocationHistoryAdmin(admin.ModelAdmin):
    list_display = ('ride', 'user', 'lat', 'lng', 'speed_kmh', 'recorded_at')
    list_filter = ('recorded_at',)
    search_fields = ('user__username',)


@admin.register(MapRoute)
class MapRouteAdmin(admin.ModelAdmin):
    list_display = ('ride', 'distance_meters', 'duration_seconds', 'calculated_at')


@admin.register(Geofence)
class GeofenceAdmin(admin.ModelAdmin):
    list_display = ('name', 'zone_type', 'is_active', 'created_at')
    list_filter = ('zone_type', 'is_active')
    list_editable = ('is_active',)
