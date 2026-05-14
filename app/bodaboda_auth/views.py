from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import graphql_jwt
from .models import CustomUser
from .serializers import KYCUploadSerializer, UserProfileSerializer
from django.shortcuts import get_object_or_404

@method_decorator(csrf_exempt, name='dispatch')
class KYCUploadView(generics.UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = KYCUploadSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

@method_decorator(csrf_exempt, name='dispatch')
class RiderDocumentUploadView(generics.UpdateAPIView):
    queryset = CustomUser.objects.filter(role='rider')
    serializer_class = KYCUploadSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self):
        rider_id = self.kwargs.get('pk')
        return get_object_or_404(CustomUser, pk=rider_id, registered_by=self.request.user)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

class ProfileView(generics.RetrieveUpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        user = authenticate(username=email, password=password)
        if user is not None:
            token = graphql_jwt.shortcuts.get_token(user)
            return Response({
                'token': token,
                'user': UserProfileSerializer(user).data
            })
        return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
