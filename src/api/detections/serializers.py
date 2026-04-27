from rest_framework import serializers
from .models import DetectionEvent

class DetectionEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = DetectionEvent
        fields = '__all__'
