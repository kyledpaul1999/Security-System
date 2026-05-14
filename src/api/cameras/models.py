from django.db import models, transaction
import uuid
from recordings.models import RetentionPolicy

class NvrDevice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    vendor = models.CharField(max_length=100, blank=True, null=True)
    model = models.CharField(max_length=100, blank=True, null=True)
    host = models.CharField(max_length=255)
    port = models.IntegerField()
    username = models.CharField(max_length=255, blank=True, null=True)
    encrypted_credentials = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, default='unknown')
    last_seen_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['host', 'port']

    def __str__(self):
        return self.name

class Camera(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nvr_device = models.ForeignKey(NvrDevice, on_delete=models.SET_NULL, blank=True, null=True, related_name='cameras')
    name = models.CharField(max_length=255)
    channel_no = models.IntegerField()
    rtsp_main_url = models.TextField(blank=True, null=True)
    rtsp_sub_url = models.TextField(blank=True, null=True)
    onvif_profile_token = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    is_enabled = models.BooleanField(default=True)
    health_status = models.CharField(max_length=50, default='unknown')
    last_health_check_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    retention_policy = models.ForeignKey(RetentionPolicy, on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.name
    def update_health_status(self, status: str):
        with transaction.atomic():
            camera = Camera.objects.select_for_update().get(pk=self.pk)
            camera.health_status = status
            camera.save()

class CameraPtzPreset(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name='ptz_presets')
    name = models.CharField(max_length=255)
    preset_token = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.camera.name} - {self.name}"
