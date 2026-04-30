import graphene
import graphql_jwt
from django.contrib.auth import get_user_model
from .inputs import UserInput, PasswordResetInput, PasswordResetConfirmInput
from .outputs import UserType
from django_rest_passwordreset.models import ResetPasswordToken
from django_rest_passwordreset.signals import reset_password_token_created

User = get_user_model()


class Register(graphene.Mutation):
    class Arguments:
        input = UserInput(required=True)

    success = graphene.Boolean()
    message = graphene.String()
    user = graphene.Field(UserType)
    token = graphene.String()

    def mutate(self, info, input):
        if User.objects.filter(email=input.email).exists():
            return Register(success=False, message="Email already registered")

        if User.objects.filter(phone=input.phone).exists():
            return Register(success=False, message="Phone number already registered")

        user = User.objects.create_user(
            username=input.email,   # use email as username
            email=input.email,
            password=input.password,
            full_name=input.full_name,
            phone=input.phone,
            role=input.role,
            license_number=input.license_number if input.license_number else None,
            plate_number=input.plate_number if input.plate_number else None,
            company_name=input.company_name if input.company_name else None,
            tax_id=input.tax_id if input.tax_id else None,
        )
        
        # Generate token for the new user
        token = graphql_jwt.shortcuts.get_token(user)
        
        return Register(success=True, message="Registration successful", user=user, token=token)


class RequestPasswordReset(graphene.Mutation):
    class Arguments:
        input = PasswordResetInput(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, input):
        try:
            user = User.objects.get(email=input.email)
            # Delete any existing tokens for this user first
            ResetPasswordToken.objects.filter(user=user).delete()
            # Create a new token — this triggers the signal that sends the email
            ResetPasswordToken.objects.create(user=user)
            return RequestPasswordReset(
                success=True,
                message="A password reset token has been sent to your email."
            )
        except User.DoesNotExist:
            # Return success=True for security (avoid email enumeration)
            return RequestPasswordReset(
                success=True,
                message="If your email is registered, you will receive a reset token."
            )


class ConfirmPasswordReset(graphene.Mutation):
    class Arguments:
        input = PasswordResetConfirmInput(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, input):
        reset_password_token = ResetPasswordToken.objects.filter(key=input.token).first()
        if not reset_password_token:
            return ConfirmPasswordReset(success=False, message="Invalid or expired token.")

        user = reset_password_token.user
        user.set_password(input.password)
        user.save()

        # Delete all tokens for this user after successful reset
        ResetPasswordToken.objects.filter(user=user).delete()

        return ConfirmPasswordReset(success=True, message="Password reset successfully. You can now login.")


class Mutation(graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    register = Register.Field()
    request_password_reset = RequestPasswordReset.Field()
    confirm_password_reset = ConfirmPasswordReset.Field()
