from rest_framework import viewsets, status, parsers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Vehicle, RiderContract
from .serializers import VehicleDocumentSerializer, RiderContractSerializer

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

@method_decorator(csrf_exempt, name='dispatch')
class FleetDocumentViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    @action(detail=True, methods=['post'], url_path='upload-docs')
    def upload_docs(self, request, pk=None):
        """Upload various vehicle documents."""
        try:
            vehicle = Vehicle.objects.get(pk=pk, owner=request.user)
        except Vehicle.DoesNotExist:
            return Response({"error": "Vehicle not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = VehicleDocumentSerializer(vehicle, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='upload-contract')
    def upload_contract(self, request, pk=None):
        """Upload a contract document for a specific contract ID."""
        try:
            contract = RiderContract.objects.get(pk=pk, owner=request.user)
        except RiderContract.DoesNotExist:
            return Response({"error": "Contract not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = RiderContractSerializer(contract, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
