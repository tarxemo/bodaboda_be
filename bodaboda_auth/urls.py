from django.urls import path, include
from .views import KYCUploadView, ProfileView

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path('kyc-upload/', KYCUploadView.as_view(), name='kyc-upload'),
    path('password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset')),
]
