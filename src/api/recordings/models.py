from django.db import models
import uuid
from identities.models import User
from cameras.models import Camera

class Recording(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
    recording_type = models.CharField(max_length=50)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    object_prefix = models.TextField()
    duration_seconds = models.IntegerField()
    total_size_bytes = models.BigIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class RecordingSegment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recording = models.ForeignKey(Recording, on_delete=models.CASCADE)
    segment_index = models.IntegerField()
    object_key = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    duration_seconds = models.IntegerField()
    checksum = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class Clip(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
    source_recording = models.ForeignKey(Recording, on_delete=models.SET_NULL, blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    object_key = models.TextField()
    exported_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class LiveStream(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    camera = models.ForeignKey(Camera, on_delete=models.CASCADE)
    stream_profile = models.CharField(max_length=100)
    status = models.CharField(max_length=50)
    hls_manifest_path = models.TextField(blank=True, null=True)
    started_at = models.DateTimeField(blank=True, null=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
