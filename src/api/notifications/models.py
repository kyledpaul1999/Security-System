from django.db import models
import uuid
from identities.models import User
from cameras.models import Camera
from detections.models import DetectionZone, DetectionEvent

class NotificationRule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE, blank=True, null=True)
    zone = models.ForeignKey(DetectionZone, on_delete=models.CASCADE, blank=True, null=True)
    event_type = models.CharField(max_length=50)
    delivery_channel = models.CharField(max_length=50)
    destination = models.TextField(blank=True, null=True)
    schedule_json = models.JSONField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rule = models.ForeignKey(NotificationRule, on_delete=models.SET_NULL, blank=True, null=True)
    detection_event = models.ForeignKey(DetectionEvent, on_delete=models.SET_NULL, blank=True, null=True)
    delivery_channel = models.CharField(max_length=50)
    destination = models.TextField()
    status = models.CharField(max_length=50)
    error_message = models.TextField(blank=True, null=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
