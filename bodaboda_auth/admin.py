from django.contrib import admin
from .models import CustomUser, Ride


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'role', 'phone', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active')
    search_fields = ('email', 'full_name', 'phone')


@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'rider', 'pickup', 'destination', 'status', 'amount', 'created_at')
    list_filter = ('status', 'payment_method')
    search_fields = ('pickup', 'destination', 'client__email', 'rider__email')
    raw_id_fields = ('client', 'rider')
