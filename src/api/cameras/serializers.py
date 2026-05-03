from rest_framework import serializers
from .models import NvrDevice, Camera, CameraPtzPreset

class NvrDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NvrDevice
        fields = '__all__'

class CameraSerializer(serializers.ModelSerializer):
    class Meta:
        model = Camera
        fields = '__all__'

class CameraPtzPresetSerializer(serializers.ModelSerializer):
    class Meta:
        model = CameraPtzPreset
        fields = '__all__'
