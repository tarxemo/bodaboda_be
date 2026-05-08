import graphene
from .models import Notification
from .inputs import MarkNotificationReadInput
from .outputs import MarkNotificationReadOutput

class MarkNotificationRead(graphene.Mutation):
    class Arguments:
        input = MarkNotificationReadInput(required=True)

    Output = MarkNotificationReadOutput

    def mutate(self, info, input):
        user = info.context.user
        if not user.is_authenticated:
            return MarkNotificationReadOutput(success=False, message="Authentication credentials were not provided")
            
        try:
            notif = Notification.objects.get(id=input.id, recipient=user)
            notif.is_read = True
            notif.save()
            return MarkNotificationReadOutput(notification=notif, success=True, message="Notification marked as read")
        except Notification.DoesNotExist:
            return MarkNotificationReadOutput(success=False, message="Notification not found")

class Mutation(graphene.ObjectType):
    mark_notification_read = MarkNotificationRead.Field()
