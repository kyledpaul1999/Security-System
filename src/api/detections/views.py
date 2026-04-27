from rest_framework import viewsets, permissions
from .models import DetectionEvent
from .serializers import DetectionEventSerializer

class DetectionEventViewSet(viewsets.ModelViewSet):
    queryset = DetectionEvent.objects.all()
    serializer_class = DetectionEventSerializer
    permission_classes = [permissions.IsAuthenticated]
