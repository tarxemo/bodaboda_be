import graphene
from bodaboda_auth.schema import Query as AuthQuery, Mutation as AuthMutation

class Query(AuthQuery, graphene.ObjectType):
    pass

class Mutation(AuthMutation, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)
