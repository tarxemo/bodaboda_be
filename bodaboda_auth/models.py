from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('client', 'Passenger'),
        ('rider', 'Rider (Driver)'),
        ('owner', 'Fleet Owner'),
        ('admin', 'Super Admin'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, unique=True)
    registered_by = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True, 
        related_name='registered_users'
    )

    # Rider Specific
    license_number = models.CharField(max_length=100, blank=True, null=True)
    plate_number = models.CharField(max_length=50, blank=True, null=True)

    # Owner Specific
    company_name = models.CharField(max_length=255, blank=True, null=True)
    tax_id = models.CharField(max_length=100, blank=True, null=True)

    # KYC Files
    nida_number = models.CharField(max_length=20, blank=True, null=True)
    id_card_front = models.FileField(upload_to='kyc/id_cards/', blank=True, null=True)
    id_card_back = models.FileField(upload_to='kyc/id_cards/', blank=True, null=True)
    license_file = models.FileField(upload_to='kyc/licenses/', blank=True, null=True)
    local_authority_letter = models.FileField(upload_to='kyc/authority_letters/', blank=True, null=True)
    business_docs = models.FileField(upload_to='kyc/business/', blank=True, null=True)

    # Guarantor Info
    guarantor_name = models.CharField(max_length=255, blank=True, null=True)
    guarantor_phone = models.CharField(max_length=20, blank=True, null=True)
    guarantor_id_front = models.FileField(upload_to='kyc/guarantor/', blank=True, null=True)
    guarantor_id_back = models.FileField(upload_to='kyc/guarantor/', blank=True, null=True)

    # Rider stats (updated on ride completion)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=5.00)
    total_trips = models.PositiveIntegerField(default=0)
    is_suspended = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} ({self.role})"


class Ride(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    PAYMENT_CHOICES = (
        ('m_pesa', 'M-Pesa'),
        ('airtel', 'Airtel Money'),
        ('tigo', 'Tigo Pesa'),
        ('wallet', 'BodaWallet'),
        ('cash', 'Cash'),
    )

    client = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='rides_as_client'
    )
    rider = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='rides_as_rider'
    )
    pickup = models.CharField(max_length=500)
    destination = models.CharField(max_length=500)
    pickup_lat = models.FloatField(null=True, blank=True)
    pickup_lng = models.FloatField(null=True, blank=True)
    dest_lat = models.FloatField(null=True, blank=True)
    dest_lng = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    distance = models.FloatField(null=True, blank=True)   # km
    duration = models.IntegerField(null=True, blank=True) # minutes
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cash')
    estimated_arrival = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Ride {self.id}: {self.pickup} → {self.destination} [{self.status}]"


class PasswordResetToken(models.Model):
    """Custom model to store password reset tokens without third-party dependencies."""
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='custom_password_reset_tokens'
    )
    key = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"PasswordResetToken for {self.user.email}"
