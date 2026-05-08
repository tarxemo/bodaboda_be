import graphene
from .queries import NotificationType

class MarkNotificationReadOutput(graphene.ObjectType):
    notification = graphene.Field(NotificationType)
    success = graphene.Boolean()
    message = graphene.String()
