import graphene
from .outputs import UserType
from django.contrib.auth import get_user_model

User = get_user_model()

class Query(graphene.ObjectType):
    me = graphene.Field(UserType)
    
    def resolve_me(self, info):
        user = info.context.user
        if user.is_anonymous:
            return None
        return user
