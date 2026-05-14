from rest_framework import viewsets
from recordings.models import Recording, Clip
from recordings.serializers import RecordingSerializer, ClipSerializer

class RecordingViewSet(viewsets.ModelViewSet):
    queryset = Recording.objects.all()
    serializer_class = RecordingSerializer

class ClipViewSet(viewsets.ModelViewSet):
    queryset = Clip.objects.all()
    serializer_class = ClipSerializer
