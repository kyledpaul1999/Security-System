from rest_framework import viewsets, permissions
from .models import NotificationRule, Notification
from .serializers import NotificationRuleSerializer, NotificationSerializer

class NotificationRuleViewSet(viewsets.ModelViewSet):
    queryset = NotificationRule.objects.all()
    serializer_class = NotificationRuleSerializer
    permission_classes = [permissions.IsAuthenticated]

class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
