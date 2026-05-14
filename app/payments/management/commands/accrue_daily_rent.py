from django.core.management.base import BaseCommand
from django.utils import timezone
from fleet.models import RiderContract
from payments.models import Wallet
from decimal import Decimal

class Command(BaseCommand):
    help = 'Accrues daily rent for all riders with active contracts'

    def handle(self, *args, **options):
        active_contracts = RiderContract.objects.filter(is_active=True)
        count = 0
        
        self.stdout.write(f"Starting debt accrual for {active_contracts.count()} active contracts...")
        
        for contract in active_contracts:
            rider = contract.rider
            wallet, created = Wallet.objects.get_or_create(user=rider)
            
            rent_amount = contract.daily_rent_tzs
            wallet.total_debt_tzs += rent_amount
            wallet.save()
            
            count += 1
            self.stdout.write(self.style.SUCCESS(f"Accrued TZS {rent_amount} for {rider.full_name}"))

        self.stdout.write(self.style.SUCCESS(f"Successfully accrued debt for {count} riders."))
