from rest_framework import viewsets, permissions
from .models import Recording, RecordingSegment, Clip, LiveStream
from .serializers import RecordingSerializer, RecordingSegmentSerializer, ClipSerializer, LiveStreamSerializer

class RecordingViewSet(viewsets.ModelViewSet):
    queryset = Recording.objects.all()
    serializer_class = RecordingSerializer
    permission_classes = [permissions.IsAuthenticated]

class RecordingSegmentViewSet(viewsets.ModelViewSet):
    queryset = RecordingSegment.objects.all()
    serializer_class = RecordingSegmentSerializer
    permission_classes = [permissions.IsAuthenticated]

class ClipViewSet(viewsets.ModelViewSet):
    queryset = Clip.objects.all()
    serializer_class = ClipSerializer
    permission_classes = [permissions.IsAuthenticated]

class LiveStreamViewSet(viewsets.ModelViewSet):
    queryset = LiveStream.objects.all()
    serializer_class = LiveStreamSerializer
    permission_classes = [permissions.IsAuthenticated]
