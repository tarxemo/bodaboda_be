import graphene
from graphene_django import DjangoObjectType
from .models import Wallet, Transaction, DailySubmission, FleetExpense

class WalletType(DjangoObjectType):
    class Meta:
        model = Wallet
        fields = "__all__"

class TransactionType(DjangoObjectType):
    class Meta:
        model = Transaction
        fields = "__all__"

class DailySubmissionType(DjangoObjectType):
    class Meta:
        model = DailySubmission
        fields = "__all__"

class FleetExpenseType(DjangoObjectType):
    class Meta:
        model = FleetExpense
        fields = "__all__"
