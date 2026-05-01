from django.db import models
from django.conf import settings
from decimal import Decimal


class Vehicle(models.Model):
    """A motorbike owned by a fleet owner and assigned to a rider."""

    STATUS_CHOICES = [
        ('active', 'Active & Deployed'),
        ('maintenance', 'Under Maintenance'),
        ('idle', 'Idle'),
        ('decommissioned', 'Decommissioned'),
    ]

    FUEL_TYPE_CHOICES = [
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric'),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='owned_vehicles', limit_choices_to={'role': 'owner'}
    )
    assigned_rider = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_vehicle',
        limit_choices_to={'role': 'rider'}
    )

    # Identity
    make = models.CharField(max_length=100, help_text="e.g. Honda, TVS")
    model_name = models.CharField(max_length=100, help_text="e.g. Boxer BM 150, HLX")
    year = models.PositiveSmallIntegerField()
    plate_number = models.CharField(max_length=50, unique=True)
    chassis_number = models.CharField(max_length=100, unique=True, blank=True, null=True)

    # Status & Fuel
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='idle', db_index=True)
    fuel_type = models.CharField(max_length=20, choices=FUEL_TYPE_CHOICES, default='petrol')
    fuel_tank_liters = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('12.00'))
    # Km per liter — used for fuel consumption calculations
    fuel_efficiency_kpl = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal('40.00'),
        help_text="Average kilometers per liter of fuel"
    )
    odometer_km = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))

    # Insurance & Docs
    insurance_policy_number = models.CharField(max_length=100, blank=True, null=True)
    insurance_expiry = models.DateField(null=True, blank=True)
    inspection_due_date = models.DateField(null=True, blank=True)

    # Documents
    logbook = models.FileField(upload_to='fleet/logbooks/', null=True, blank=True)
    insurance_doc = models.FileField(upload_to='fleet/insurance/', null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Vehicle"
        verbose_name_plural = "Fleet Vehicles"

    def __str__(self):
        return f"{self.make} {self.model_name} [{self.plate_number}] — {self.get_status_display()}"


class MaintenanceLog(models.Model):
    """Records vehicle maintenance and repair events."""

    TYPE_CHOICES = [
        ('service', 'Routine Service'),
        ('repair', 'Repair'),
        ('tyre', 'Tyre Change'),
        ('oil_change', 'Oil Change'),
        ('inspection', 'Inspection'),
        ('other', 'Other'),
    ]

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='maintenance_logs')
    maintenance_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.TextField()
    cost_tzs = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    odometer_at_service_km = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    performed_by = models.CharField(max_length=255, blank=True, null=True, help_text="Garage or technician name")
    performed_at = models.DateField()
    next_service_due_km = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    next_service_due_date = models.DateField(null=True, blank=True)
    receipt = models.FileField(upload_to='fleet/maintenance_receipts/', null=True, blank=True)
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_maintenance_type_display()} on {self.vehicle} @ {self.performed_at}"


class FuelLog(models.Model):
    """Records every fuel refill event for a vehicle."""

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='fuel_logs')
    rider = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='fuel_logs'
    )
    liters_added = models.DecimalField(max_digits=7, decimal_places=2)
    cost_per_liter_tzs = models.DecimalField(max_digits=8, decimal_places=2)
    total_cost_tzs = models.DecimalField(max_digits=12, decimal_places=2)
    odometer_at_fill_km = models.DecimalField(max_digits=10, decimal_places=2)
    station_name = models.CharField(max_length=255, blank=True, null=True)
    refilled_at = models.DateTimeField()
    receipt_image = models.ImageField(upload_to='fleet/fuel_receipts/', null=True, blank=True)

    def __str__(self):
        return f"{self.liters_added}L for {self.vehicle} — TZS {self.total_cost_tzs}"


class FuelPrice(models.Model):
    """Tracks daily fuel pump prices (used for fare and cost calculations)."""

    FUEL_TYPE_CHOICES = [
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
    ]

    fuel_type = models.CharField(max_length=20, choices=FUEL_TYPE_CHOICES)
    price_per_liter_tzs = models.DecimalField(max_digits=10, decimal_places=2)
    region = models.CharField(max_length=100, default='Dar es Salaam')
    effective_date = models.DateField(db_index=True)
    source = models.CharField(max_length=255, blank=True, null=True, help_text="Source of price data")
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-effective_date']
        unique_together = ('fuel_type', 'effective_date', 'region')
        verbose_name = "Fuel Price Record"

    def __str__(self):
        return f"{self.get_fuel_type_display()} @ TZS {self.price_per_liter_tzs}/L — {self.effective_date}"
