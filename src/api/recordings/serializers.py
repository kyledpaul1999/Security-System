from rest_framework import serializers
from recordings.models import Recording, Clip, LiveStream

class RecordingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recording
        fields = '__all__'

class ClipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clip
        fields = '__all__'

class LiveStreamStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = LiveStream
        fields = ('camera', 'status', 'hls_manifest_path', 'stream_profile')
