from rest_framework import serializers
from .models import Recording, RecordingSegment, Clip, LiveStream

class RecordingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recording
        fields = '__all__'

class RecordingSegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecordingSegment
        fields = '__all__'

class ClipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clip
        fields = '__all__'

class LiveStreamSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiveStream
        fields = '__all__'
