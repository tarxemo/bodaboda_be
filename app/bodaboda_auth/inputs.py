import graphene
from .models import CustomUser

class UserInput(graphene.InputObjectType):
    full_name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String(required=True)
    password = graphene.String(required=True)
    role = graphene.String(required=True)
    license_number = graphene.String()
    plate_number = graphene.String()
    company_name = graphene.String()
    tax_id = graphene.String()

class PasswordResetInput(graphene.InputObjectType):
    email = graphene.String(required=True)

class PasswordResetConfirmInput(graphene.InputObjectType):
    token = graphene.String(required=True)
    password = graphene.String(required=True)
