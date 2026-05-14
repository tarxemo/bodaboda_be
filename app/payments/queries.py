import graphene
from .outputs import WalletType, TransactionType, DailySubmissionType, FleetExpenseType
from .models import Wallet, Transaction, DailySubmission, FleetExpense

class Query(graphene.ObjectType):
    my_wallet = graphene.Field(WalletType)
    my_transactions = graphene.List(TransactionType)
    my_submissions = graphene.List(DailySubmissionType)
    received_submissions = graphene.List(DailySubmissionType)
    my_expenses = graphene.List(FleetExpenseType)

    def resolve_my_wallet(self, info):
        user = info.context.user
        if user.is_authenticated:
            wallet, created = Wallet.objects.get_or_create(user=user)
            return wallet
        return None

    def resolve_my_transactions(self, info):
        user = info.context.user
        if user.is_authenticated:
            return Transaction.objects.filter(wallet__user=user).order_by('-created_at')
        return []

    def resolve_my_submissions(self, info):
        user = info.context.user
        if user.is_authenticated and user.role == 'rider':
            return DailySubmission.objects.filter(rider=user).order_by('-submission_date')
        return []

    def resolve_received_submissions(self, info):
        user = info.context.user
        if user.is_authenticated and user.role == 'owner':
            return DailySubmission.objects.filter(owner=user).order_by('-submission_date')
        return []

    def resolve_my_expenses(self, info):
        user = info.context.user
        if user.is_authenticated:
            return FleetExpense.objects.filter(user=user).order_by('-expense_date')
        return []
