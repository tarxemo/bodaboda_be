from django.db import models
from django.conf import settings

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('SYSTEM', 'System Alert'),
        ('RIDE_REQUEST', 'Ride Request'),
        ('RIDE_ACCEPTED', 'Ride Accepted'),
        ('RIDE_CANCELLED', 'Ride Cancelled'),
        ('PAYMENT', 'Payment Alert'),
        ('MESSAGE', 'Message Alert')
    ]
    
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='SYSTEM')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.recipient} - {self.title}"
