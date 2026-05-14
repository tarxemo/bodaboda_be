from rest_framework import authentication, exceptions
from django.contrib.auth import authenticate
from graphql_jwt.utils import get_http_authorization

class GraphQLJWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        if get_http_authorization(request) is not None:
            user = authenticate(request=request)
            if user is not None:
                return (user, None)
        return None
