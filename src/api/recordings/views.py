from rest_framework import viewsets, permissions
from .models import Recording, LiveStream
from .serializers import RecordingSerializer, LiveStreamSerializer

class RecordingViewSet(viewsets.ModelViewSet):
    queryset = Recording.objects.all()
    serializer_class = RecordingSerializer
    permission_classes = [permissions.IsAuthenticated]

class LiveStreamViewSet(viewsets.ModelViewSet):
    queryset = LiveStream.objects.all()
    serializer_class = LiveStreamSerializer
    permission_classes = [permissions.IsAuthenticated]
