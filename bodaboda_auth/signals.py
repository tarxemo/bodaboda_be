from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django_rest_passwordreset.signals import reset_password_token_created

@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, *args, **kwargs):
    """
    Handles password reset tokens
    When a token is created, an e-mail should be sent to the user
    :param sender: View Class that sent the signal
    :param instance: View Instance that sent the signal
    :param reset_password_token: Token Model Instance
    :param args:
    :param kwargs:
    :return:
    """
    # send an e-mail to the user
    context = {
        'current_user': reset_password_token.user,
        'username': reset_password_token.user.username,
        'email': reset_password_token.user.email,
        'token': reset_password_token.key
    }

    # render email text
    email_html_message = render_to_string('bodaboda_auth/password_reset_email.html', context)
    email_plaintext_message = strip_tags(email_html_message)

    msg = EmailMultiAlternatives(
        # title:
        "Password Reset for BodaKitaa",
        # message:
        email_plaintext_message,
        # from:
        "BodaKitaa <martinsanga230@gmail.com>",
        # to:
        [reset_password_token.user.email]
    )
    msg.attach_alternative(email_html_message, "text/html")
    msg.send()
