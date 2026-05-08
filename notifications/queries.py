import graphene
from graphene_django.types import DjangoObjectType
from .models import Notification

class NotificationType(DjangoObjectType):
    class Meta:
        model = Notification
        fields = '__all__'

class Query(graphene.ObjectType):
    my_notifications = graphene.List(NotificationType)

    def resolve_my_notifications(self, info):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception("Authentication credentials were not provided")
        return Notification.objects.filter(recipient=user)
