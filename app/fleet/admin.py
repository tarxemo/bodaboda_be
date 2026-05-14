from django.contrib import admin
from .models import Vehicle, MaintenanceLog, FuelLog, FuelPrice


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('plate_number', 'make', 'model_name', 'year', 'owner', 'assigned_rider', 'status', 'fuel_efficiency_kpl', 'odometer_km')
    list_filter = ('status', 'fuel_type', 'make')
    search_fields = ('plate_number', 'chassis_number', 'owner__username', 'assigned_rider__username')
    list_editable = ('status',)


@admin.register(MaintenanceLog)
class MaintenanceLogAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'maintenance_type', 'cost_tzs', 'performed_at', 'next_service_due_date')
    list_filter = ('maintenance_type', 'performed_at')
    search_fields = ('vehicle__plate_number',)


@admin.register(FuelLog)
class FuelLogAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'rider', 'liters_added', 'cost_per_liter_tzs', 'total_cost_tzs', 'odometer_at_fill_km', 'refilled_at')
    list_filter = ('refilled_at',)
    search_fields = ('vehicle__plate_number', 'rider__username')


@admin.register(FuelPrice)
class FuelPriceAdmin(admin.ModelAdmin):
    list_display = ('fuel_type', 'price_per_liter_tzs', 'region', 'effective_date', 'source')
    list_filter = ('fuel_type', 'region')
    date_hierarchy = 'effective_date'
