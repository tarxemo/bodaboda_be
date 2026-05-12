import graphene
from graphene_django import DjangoObjectType
from .models import Wallet, Transaction
from django.db.models import Sum

class WalletType(DjangoObjectType):
    class Meta:
        model = Wallet
        fields = "__all__"

class TransactionType(DjangoObjectType):
    class Meta:
        model = Transaction
        fields = "__all__"

class Query(graphene.ObjectType):
    my_wallet = graphene.Field(WalletType)
    my_transactions = graphene.List(TransactionType)

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

class Mutation(graphene.ObjectType):
    # Add mutations like top-up if needed later
    pass
