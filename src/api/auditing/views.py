from rest_framework import viewsets, permissions
from .models import AuditLog, SystemHealthEvent
from .serializers import AuditLogSerializer, SystemHealthEventSerializer

class AuditLogViewSet(viewsets.ModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAdminUser]

class SystemHealthEventViewSet(viewsets.ModelViewSet):
    queryset = SystemHealthEvent.objects.all()
    serializer_class = SystemHealthEventSerializer
    permission_classes = [permissions.IsAdminUser]
