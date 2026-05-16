import graphene
import graphql_jwt
from graphql_jwt.shortcuts import get_token
import secrets
import string
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.conf import settings
from .inputs import UserInput, PasswordResetInput, PasswordResetConfirmInput
from .outputs import UserType
from .models import PasswordResetToken

User = get_user_model()


def generate_token(length=8):
    """Generate a secure human-readable reset token (uppercase + digits, no ambiguous chars)."""
    alphabet = string.ascii_uppercase.replace('O', '').replace('I', '') + string.digits.replace('0', '').replace('1', '')
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def send_password_reset_email(user, token_key):
    """Sends a premium branded HTML email with the password reset token."""
    full_name = getattr(user, 'full_name', user.username) or user.username
    from_email = settings.DEFAULT_FROM_EMAIL

    html_message = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Reset Your BodaKitaa Password</title>
</head>
<body style="margin:0;padding:0;background-color:#0f0f13;font-family:'Segoe UI',Tahoma,Geneva,Verdana,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#0f0f13;padding:40px 0;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">

          <!-- Logo Header -->
          <tr>
            <td align="center" style="padding:0 0 32px 0;">
              <table cellpadding="0" cellspacing="0">
                <tr>
                  <td style="background:linear-gradient(135deg,#FE7743,#E65C2E);border-radius:16px;padding:14px 28px;display:inline-block;">
                    <span style="font-size:22px;font-weight:900;color:#ffffff;letter-spacing:-0.5px;">🏍 BodaKitaa</span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Main Card -->
          <tr>
            <td style="background:linear-gradient(145deg,#1a1a2e,#16213e);border-radius:28px;padding:48px 48px 40px;border:1px solid rgba(254,119,67,0.15);box-shadow:0 25px 50px rgba(0,0,0,0.5);">

              <!-- Icon -->
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td align="center" style="padding-bottom:28px;">
                    <div style="background:rgba(254,119,67,0.12);border:1px solid rgba(254,119,67,0.3);border-radius:50%;width:72px;height:72px;display:inline-flex;align-items:center;justify-content:center;font-size:32px;">
                      🔐
                    </div>
                  </td>
                </tr>

                <!-- Title -->
                <tr>
                  <td align="center" style="padding-bottom:12px;">
                    <h1 style="margin:0;font-size:30px;font-weight:900;color:#ffffff;letter-spacing:-0.5px;line-height:1.2;">Password Reset Request</h1>
                  </td>
                </tr>

                <!-- Subtitle -->
                <tr>
                  <td align="center" style="padding-bottom:36px;">
                    <p style="margin:0;font-size:16px;color:#94a3b8;line-height:1.6;">Hello, <strong style="color:#e2e8f0;">{full_name}</strong>. We received a request to reset your password.</p>
                  </td>
                </tr>

                <!-- Divider -->
                <tr>
                  <td style="padding-bottom:32px;">
                    <hr style="border:none;border-top:1px solid rgba(255,255,255,0.08);margin:0;" />
                  </td>
                </tr>

                <!-- Token Label -->
                <tr>
                  <td align="center" style="padding-bottom:16px;">
                    <p style="margin:0;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:3px;color:#64748b;">Your Verification Token</p>
                  </td>
                </tr>

                <!-- Token Box -->
                <tr>
                  <td align="center" style="padding-bottom:32px;">
                    <table cellpadding="0" cellspacing="0">
                      <tr>
                        <td style="background:linear-gradient(135deg,rgba(254,119,67,0.15),rgba(230,92,46,0.1));border:2px solid rgba(254,119,67,0.4);border-radius:16px;padding:20px 40px;text-align:center;">
                          <span style="font-family:'Courier New',Courier,monospace;font-size:36px;font-weight:900;color:#FE7743;letter-spacing:8px;display:block;">{token_key}</span>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>

                <!-- Instructions -->
                <tr>
                  <td style="padding-bottom:36px;">
                    <table width="100%" cellpadding="0" cellspacing="0" style="background:rgba(255,255,255,0.03);border-radius:12px;padding:20px;border:1px solid rgba(255,255,255,0.06);">
                      <tr>
                        <td style="padding:16px;">
                          <p style="margin:0 0 10px;font-size:13px;color:#94a3b8;line-height:1.7;">
                            ✅ &nbsp;Enter this token in the reset password form.<br/>
                            ⏳ &nbsp;This token expires in <strong style="color:#e2e8f0;">24 hours</strong>.<br/>
                            🔒 &nbsp;Never share this token with anyone.
                          </p>
                        </td>
                      </tr>
                    </table>
                  </td>
                </tr>

                <!-- Divider -->
                <tr>
                  <td style="padding-bottom:28px;">
                    <hr style="border:none;border-top:1px solid rgba(255,255,255,0.08);margin:0;" />
                  </td>
                </tr>

                <!-- Security notice -->
                <tr>
                  <td align="center">
                    <p style="margin:0;font-size:13px;color:#475569;line-height:1.6;">
                      If you didn't request this, please ignore this email.<br/>
                      Your account remains secure.
                    </p>
                  </td>
                </tr>

              </table>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td align="center" style="padding:28px 0 0;">
              <p style="margin:0 0 6px;font-size:13px;color:#475569;">© 2026 BodaKitaa. All rights reserved.</p>
              <p style="margin:0;font-size:12px;color:#334155;">Sent from <a href="mailto:{from_email}" style="color:#FE7743;text-decoration:none;">{from_email}</a></p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

    plain_message = f"""BodaKitaa — Password Reset Request

Hello {full_name},

Your password reset token is:

    {token_key}

Enter this token in the password reset form to set your new password.

This token expires in 24 hours. If you didn't request this, please ignore this email.

— The BodaKitaa Team
"""

    msg = EmailMultiAlternatives(
        subject="🔐 BodaKitaa — Your Password Reset Token",
        body=plain_message,
        from_email=from_email,
        to=[user.email],
    )
    msg.attach_alternative(html_message, "text/html")
    msg.send()


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
            username=input.email,
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

        token = get_token(user)
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
            PasswordResetToken.objects.filter(user=user).delete()

            # Generate a human-friendly token and save it
            token_key = generate_token(8)
            PasswordResetToken.objects.create(user=user, key=token_key)

            # Send the premium email directly (not via signal)
            send_password_reset_email(user, token_key)

            return RequestPasswordReset(
                success=True,
                message="A password reset token has been sent to your email."
            )
        except User.DoesNotExist:
            return RequestPasswordReset(
                success=True,
                message="If your email is registered, you will receive a reset token."
            )
        except Exception as e:
            return RequestPasswordReset(
                success=False,
                message=f"Failed to send reset email. Please try again later."
            )


class ConfirmPasswordReset(graphene.Mutation):
    class Arguments:
        input = PasswordResetConfirmInput(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, input):
        reset_password_token = PasswordResetToken.objects.filter(key=input.token.upper()).first()
        if not reset_password_token:
            return ConfirmPasswordReset(success=False, message="Invalid or expired token.")

        user = reset_password_token.user
        user.set_password(input.password)
        user.save()

        PasswordResetToken.objects.filter(user=user).delete()

        return ConfirmPasswordReset(success=True, message="Password reset successfully. You can now login.")


class RegisterRider(graphene.Mutation):
    class Arguments:
        full_name = graphene.String(required=True)
        phone = graphene.String(required=True)
        email = graphene.String()
        password = graphene.String(required=True)
        license_number = graphene.String()
        nida_number = graphene.String()
        guarantor_name = graphene.String()
        guarantor_phone = graphene.String()

    success = graphene.Boolean()
    message = graphene.String()
    user = graphene.Field(UserType)

    def mutate(self, info, **kwargs):
        owner = info.context.user
        if not owner.is_authenticated or owner.role != 'owner':
            return RegisterRider(success=False, message="Only owners can register riders.")

        phone = kwargs.get('phone')
        if User.objects.filter(phone=phone).exists():
            return RegisterRider(success=False, message="Phone number already registered.")

        full_name = kwargs.get('full_name')
        provided_email = kwargs.get('email', '').strip()
        email = provided_email if provided_email else f"{phone}@bodakitaa.com"
        password = kwargs.get('password')

        if User.objects.filter(email=email).exists():
            return RegisterRider(success=False, message="Email already registered.")

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            full_name=full_name,
            phone=phone,
            role='employed_rider',
            registered_by=owner,
            license_number=kwargs.get('license_number'),
            nida_number=kwargs.get('nida_number'),
            guarantor_name=kwargs.get('guarantor_name'),
            guarantor_phone=kwargs.get('guarantor_phone')
        )
        return RegisterRider(success=True, message="Employed rider registered successfully.", user=user)



class ToggleRiderSuspension(graphene.Mutation):
    class Arguments:
        rider_id = graphene.Int(required=True)

    success = graphene.Boolean()
    message = graphene.String()
    is_suspended = graphene.Boolean()

    def mutate(self, info, rider_id):
        owner = info.context.user
        if not owner.is_authenticated or owner.role != 'owner':
            return ToggleRiderSuspension(success=False, message="Not authorized.")
        
        try:
            rider = User.objects.get(pk=rider_id, registered_by=owner)
            rider.is_suspended = not rider.is_suspended
            rider.save()
            status_text = "suspended" if rider.is_suspended else "reinstated"
            return ToggleRiderSuspension(
                success=True, 
                message=f"Rider {rider.full_name} has been {status_text}.",
                is_suspended=rider.is_suspended
            )
        except User.DoesNotExist:
            return ToggleRiderSuspension(success=False, message="Rider not found or not registered by you.")

class SetRiderDailyTarget(graphene.Mutation):
    """Owner sets the daily amount an employed rider must submit."""
    class Arguments:
        rider_id = graphene.Int(required=True)
        daily_target_tzs = graphene.Float(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, rider_id, daily_target_tzs):
        owner = info.context.user
        if not owner.is_authenticated or owner.role != 'owner':
            return SetRiderDailyTarget(success=False, message="Not authorized.")
        try:
            rider = User.objects.get(pk=rider_id, registered_by=owner)
            rider.daily_target_tzs = daily_target_tzs
            rider.save()
            return SetRiderDailyTarget(success=True, message="Daily target updated.")
        except User.DoesNotExist:
            return SetRiderDailyTarget(success=False, message="Rider not found.")


class ContactUs(graphene.Mutation):
    class Arguments:
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)
        email = graphene.String(required=True)
        message = graphene.String(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, first_name, last_name, email, message):
        try:
            from django.core.mail import EmailMessage
            from django.conf import settings
            
            email_body = f"""
New Contact Message from BodaKitaa

Name: {first_name} {last_name}
Email: {email}

Message:
{message}
"""
            msg = EmailMessage(
                subject=f"New Contact from {first_name} {last_name}",
                body=email_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=['bodakitaa360@gmail.com'],
                reply_to=[email]
            )
            msg.send(fail_silently=False)
            
            return ContactUs(success=True, message="Message sent successfully.")
        except Exception as e:
            return ContactUs(success=False, message=str(e))

class Mutation(graphene.ObjectType):
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    register = Register.Field()
    register_rider = RegisterRider.Field()
    toggle_rider_suspension = ToggleRiderSuspension.Field()
    set_rider_daily_target = SetRiderDailyTarget.Field()
    request_password_reset = RequestPasswordReset.Field()
    confirm_password_reset = ConfirmPasswordReset.Field()
    contact_us = ContactUs.Field()
