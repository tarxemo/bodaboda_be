from django.urls import path
from .views import RideEstimateView, RideRequestListCreateView, RideDetailView, RideRateView

urlpatterns = [
    path('', RideRequestListCreateView.as_view(), name='ride-list-create'),
    path('<int:pk>/', RideDetailView.as_view(), name='ride-detail'),
    path('estimate/', RideEstimateView.as_view(), name='ride-estimate'),
    path('<int:pk>/rate/', RideRateView.as_view(), name='ride-rate'),
]
