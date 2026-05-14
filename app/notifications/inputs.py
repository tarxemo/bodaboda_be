import graphene

class MarkNotificationReadInput(graphene.InputObjectType):
    id = graphene.ID(required=True)
