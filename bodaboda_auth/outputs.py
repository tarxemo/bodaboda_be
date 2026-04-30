import graphene
from graphene_django import DjangoObjectType
from .models import CustomUser

class UserType(DjangoObjectType):
    class Meta:
        model = CustomUser
        fields = ("id", "username", "email", "full_name", "phone", "role", 
                  "license_number", "plate_number", "company_name", "tax_id")

class AuthResponse(graphene.ObjectType):
    success = graphene.Boolean()
    message = graphene.String()
    user = graphene.Field(UserType)
