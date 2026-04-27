from rest_framework import serializers
from .models import AuditLog, SystemHealthEvent

class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = '__all__'

class SystemHealthEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemHealthEvent
        fields = '__all__'
