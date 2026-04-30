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
    
    # Rider Specific
    license_number = models.CharField(max_length=100, blank=True, null=True)
    plate_number = models.CharField(max_length=50, blank=True, null=True)
    
    # Owner Specific
    company_name = models.CharField(max_length=255, blank=True, null=True)
    tax_id = models.CharField(max_length=100, blank=True, null=True)
    
    # KYC Files
    id_card_front = models.FileField(upload_to='kyc/id_cards/', blank=True, null=True)
    id_card_back = models.FileField(upload_to='kyc/id_cards/', blank=True, null=True)
    license_file = models.FileField(upload_to='kyc/licenses/', blank=True, null=True)
    business_docs = models.FileField(upload_to='kyc/business/', blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"
