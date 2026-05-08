import graphene
from bodaboda_auth.schema import Query as AuthQuery, Mutation as AuthMutation
from rides.schema import Query as RidesQuery, Mutation as RidesMutation
from notifications.schema import Query as NotificationsQuery, Mutation as NotificationsMutation
from fleet.schema import Query as FleetQuery, Mutation as FleetMutation

class Query(AuthQuery, RidesQuery,NotificationsQuery, FleetQuery, graphene.ObjectType):
    pass

class Mutation(AuthMutation, RidesMutation, NotificationsMutation, FleetMutation, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)
