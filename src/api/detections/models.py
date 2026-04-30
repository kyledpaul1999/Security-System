from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid
from cameras.models import Camera
from timescale.db.models.models import TimescaleModel

class DetectionZone(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name='detection_zones')
    name = models.CharField(max_length=255)
    polygon = models.JSONField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.camera.name} - {self.name}"

class DetectionPolicy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, blank=True, null=True)
    zone = models.ForeignKey(DetectionZone, on_delete=models.CASCADE, blank=True, null=True)
    object_type = models.CharField(max_length=50, default='person')
    min_confidence = models.DecimalField(max_digits=4, decimal_places=3, default=0.7, validators=[MinValueValidator(0), MaxValueValidator(1)])
    cooldown_seconds = models.IntegerField(default=60)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class DetectionEvent(TimescaleModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, related_name='detection_events')
    zone = models.ForeignKey(DetectionZone, on_delete=models.SET_NULL, blank=True, null=True)
    event_type = models.CharField(max_length=50)
    confidence = models.DecimalField(max_digits=4, decimal_places=3)
    snapshot_object_key = models.TextField(blank=True, null=True)
    frame_ts = models.DateTimeField()
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("id", "time"),)
