from django.db import models
from django.conf import settings
from decimal import Decimal


class Wallet(models.Model):
    """BodaKitaa in-app wallet for every user."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='wallet'
    )
    balance_tzs = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0.00'))
    is_frozen = models.BooleanField(default=False, help_text="Freeze wallet on suspicious activity")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Wallet of {self.user} — TZS {self.balance_tzs}"


class Transaction(models.Model):
    """Every financial movement (credit/debit) on a wallet."""

    TYPE_CHOICES = [
        ('top_up', 'Top Up'),
        ('ride_payment', 'Ride Payment'),
        ('ride_earning', 'Ride Earning'),
        ('withdrawal', 'Withdrawal'),
        ('refund', 'Refund'),
        ('commission', 'Platform Commission'),
        ('adjustment', 'Manual Adjustment'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('reversed', 'Reversed'),
    ]

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    ride = models.ForeignKey(
        'rides.RideRequest', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='transactions'
    )
    transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES, db_index=True)
    amount_tzs = models.DecimalField(max_digits=14, decimal_places=2)
    # Running balance snapshot after this transaction
    balance_after_tzs = models.DecimalField(max_digits=14, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', db_index=True)
    # For mobile money payments
    external_reference = models.CharField(max_length=255, blank=True, null=True, db_index=True)
    payment_provider = models.CharField(
        max_length=50, blank=True, null=True,
        help_text="e.g. M-Pesa, Airtel Money, Tigo Pesa"
    )
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.transaction_type}] TZS {self.amount_tzs} — {self.status}"


class CommissionRule(models.Model):
    """Defines how much the platform takes from each ride."""

    name = models.CharField(max_length=100)
    percentage = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal('15.00'),
        help_text="Commission percentage deducted from rider earnings"
    )
    is_active = models.BooleanField(default=True)
    applies_to_role = models.CharField(
        max_length=20, default='rider',
        help_text="User role this rule applies to"
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Commission Rule: {self.percentage}% ({self.name})"


class LoyaltyAccount(models.Model):
    """Tracks loyalty points earned by clients."""

    TIER_CHOICES = [
        ('bronze', 'Bronze'),
        ('silver', 'Silver'),
        ('gold', 'Gold'),
        ('platinum', 'Platinum'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='loyalty'
    )
    points = models.IntegerField(default=0)
    tier = models.CharField(max_length=20, choices=TIER_CHOICES, default='bronze')
    total_rides = models.IntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Loyalty: {self.user} — {self.points} pts ({self.tier})"


class LoyaltyTransaction(models.Model):
    """Records when points are earned or redeemed."""

    TYPE_CHOICES = [
        ('earned', 'Points Earned'),
        ('redeemed', 'Points Redeemed'),
        ('expired', 'Points Expired'),
        ('bonus', 'Bonus Points'),
    ]

    account = models.ForeignKey(LoyaltyAccount, on_delete=models.CASCADE, related_name='transactions')
    ride = models.ForeignKey(
        'rides.RideRequest', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='loyalty_transactions'
    )
    transaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    points = models.IntegerField()
    description = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.transaction_type}] {self.points} pts for {self.account.user}"
