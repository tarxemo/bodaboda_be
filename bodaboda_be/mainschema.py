import graphene
from bodaboda_auth.schema import Query as AuthQuery, Mutation as AuthMutation
from rides.schema import Query as RidesQuery, Mutation as RidesMutation

class Query(AuthQuery, RidesQuery, graphene.ObjectType):
    pass

class Mutation(AuthMutation, RidesMutation, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)
