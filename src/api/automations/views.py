from rest_framework import viewsets, permissions
from .models import AutomationRule, AutomationRun, AutomationActionRun
from .serializers import AutomationRuleSerializer, AutomationRunSerializer, AutomationActionRunSerializer

class AutomationRuleViewSet(viewsets.ModelViewSet):
    queryset = AutomationRule.objects.all()
    serializer_class = AutomationRuleSerializer
    permission_classes = [permissions.IsAuthenticated]

class AutomationRunViewSet(viewsets.ModelViewSet):
    queryset = AutomationRun.objects.all()
    serializer_class = AutomationRunSerializer
    permission_classes = [permissions.IsAuthenticated]

class AutomationActionRunViewSet(viewsets.ModelViewSet):
    queryset = AutomationActionRun.objects.all()
    serializer_class = AutomationActionRunSerializer
    permission_classes = [permissions.IsAuthenticated]
