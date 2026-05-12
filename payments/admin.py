from django.contrib import admin
from .models import Wallet, Transaction, CommissionRule, LoyaltyAccount, LoyaltyTransaction


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance_tzs', 'is_frozen', 'updated_at')
    list_filter = ('is_frozen',)
    search_fields = ('user__username',)
    list_editable = ('is_frozen',)


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('wallet', 'transaction_type', 'amount_tzs', 'balance_after_tzs', 'status', 'payment_provider', 'created_at')
    list_filter = ('transaction_type', 'status', 'payment_provider')
    search_fields = ('wallet__user__username', 'external_reference')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'


@admin.register(CommissionRule)
class CommissionRuleAdmin(admin.ModelAdmin):
    list_display = ('name', 'percentage', 'applies_to_role', 'is_active', 'updated_at')
    list_editable = ('is_active', 'percentage')


@admin.register(LoyaltyAccount)
class LoyaltyAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'points', 'tier', 'total_rides', 'updated_at')
    list_filter = ('tier',)
    search_fields = ('user__username',)


@admin.register(LoyaltyTransaction)
class LoyaltyTransactionAdmin(admin.ModelAdmin):
    list_display = ('account', 'transaction_type', 'points', 'description', 'created_at')
    list_filter = ('transaction_type',)
