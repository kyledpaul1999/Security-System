from rest_framework import viewsets, permissions
from .models import Camera, NvrDevice, CameraPtzPreset
from .serializers import CameraSerializer, NvrDeviceSerializer, CameraPtzPresetSerializer

class NvrDeviceViewSet(viewsets.ModelViewSet):
    queryset = NvrDevice.objects.all()
    serializer_class = NvrDeviceSerializer
    permission_classes = [permissions.IsAuthenticated]

class CameraViewSet(viewsets.ModelViewSet):
    queryset = Camera.objects.all()
    serializer_class = CameraSerializer
    permission_classes = [permissions.IsAuthenticated]

class CameraPtzPresetViewSet(viewsets.ModelViewSet):
    queryset = CameraPtzPreset.objects.all()
    serializer_class = CameraPtzPresetSerializer
    permission_classes = [permissions.IsAuthenticated]
