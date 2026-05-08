import graphene
from .queries import Query as NotificationQuery
from .mutations import Mutation as NotificationMutation

class Query(NotificationQuery, graphene.ObjectType):
    pass

class Mutation(NotificationMutation, graphene.ObjectType):
    pass
