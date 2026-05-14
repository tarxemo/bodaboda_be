import graphene
from .queries import Query as AuthQuery
from .mutations import Mutation as AuthMutation

class Query(AuthQuery, graphene.ObjectType):
    pass

class Mutation(AuthMutation, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)
