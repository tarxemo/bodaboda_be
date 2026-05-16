from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class EmailOrPhoneBackend(ModelBackend):
    """
    Custom authentication backend that allows users to log in using 
    either their email/username or their phone number.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)
        
        try:
            # Check for user by email (username field) or phone
            user = User.objects.get(Q(email__iexact=username) | Q(phone=username) | Q(username=username))
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            # If multiple, pick the first one (shouldn't happen with unique constraints)
            user = User.objects.filter(Q(email__iexact=username) | Q(phone=username) | Q(username=username)).first()

        if user and user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
