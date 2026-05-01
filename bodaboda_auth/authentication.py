from rest_framework import authentication, exceptions
from graphql_jwt.backends import JSONWebTokenBackend
from graphql_jwt.exceptions import JSONWebTokenError
from django.utils.translation import gettext_lazy as _

class JSONWebTokenAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        try:
            user = JSONWebTokenBackend().authenticate(request)
            if user is not None:
                return (user, None)
        except JSONWebTokenError as e:
            raise exceptions.AuthenticationFailed(_(str(e)))
        return None
