from django.db import models, transaction
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

    @classmethod
    def create_recording(cls, camera, recording_type, start_time, end_time, object_prefix, duration_seconds, total_size_bytes):
        with transaction.atomic(isolation='SERIALIZABLE'):
            # Example check: limit to 10 recordings per camera
            if Recording.objects.filter(camera=camera).count() >= 10:
                raise Exception('Maximum number of recordings reached for this camera.')

            return cls.objects.create(
                camera=camera,
                recording_type=recording_type,
                start_time=start_time,
                end_time=end_time,
                object_prefix=object_prefix,
                duration_seconds=duration_seconds,
                total_size_bytes=total_size_bytes,
            )


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

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['camera'],
                condition=models.Q(status='active'),
                name='unique_active_stream_per_camera'
            )
        ]
