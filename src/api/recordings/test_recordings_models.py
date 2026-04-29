
import pytest
from django.utils import timezone
from django.core.exceptions import ValidationError
from cameras.models import Camera
from identities.models import User
from recordings.models import Recording, RecordingSegment, Clip

@pytest.fixture
def camera():
    return Camera.objects.create(name="Test Camera", channel_no=1)

@pytest.fixture
def user():
    return User.objects.create_user(username="testuser", password="password")

@pytest.mark.django_db
class TestRecordingModel:

    def test_create_recording(self, camera):
        """Test creating a Recording instance."""
        recording = Recording.objects.create(
            camera=camera,
            recording_type="manual",
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(minutes=1),
            object_prefix="rec/123/",
            duration_seconds=60
        )
        assert recording.pk is not None
        assert recording.camera == camera

    def test_delete_camera_cascades_to_recordings(self, camera):
        """Test that deleting a camera also deletes its recordings."""
        Recording.objects.create(camera=camera, recording_type="motion", start_time=timezone.now(), end_time=timezone.now(), object_prefix="rec/", duration_seconds=1)
        assert Recording.objects.count() == 1
        camera.delete()
        assert Recording.objects.count() == 0

@pytest.mark.django_db
class TestRecordingSegmentModel:

    def test_create_segment(self, camera):
        """Test creating a RecordingSegment."""
        recording = Recording.objects.create(camera=camera, recording_type="scheduled", start_time=timezone.now(), end_time=timezone.now(), object_prefix="rec/", duration_seconds=30)
        segment = RecordingSegment.objects.create(
            recording=recording,
            segment_index=1,
            object_key="rec/123/seg1.ts",
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(seconds=10),
            duration_seconds=10
        )
        assert segment.pk is not None
        assert recording.recordingsegment_set.count() == 1

    def test_delete_recording_cascades_to_segments(self, camera):
        """Test that deleting a recording deletes its segments."""
        recording = Recording.objects.create(camera=camera, recording_type="continuous", start_time=timezone.now(), end_time=timezone.now(), object_prefix="rec/", duration_seconds=1)
        RecordingSegment.objects.create(recording=recording, segment_index=0, object_key="key", start_time=timezone.now(), end_time=timezone.now(), duration_seconds=1)
        assert RecordingSegment.objects.count() == 1
        recording.delete()
        assert RecordingSegment.objects.count() == 0

@pytest.mark.django_db
class TestClipModel:

    def test_create_clip(self, camera, user):
        """Test creating a Clip."""
        clip = Clip.objects.create(
            camera=camera,
            start_time=timezone.now(),
            end_time=timezone.now(),
            object_key="clips/abc.mp4",
            exported_by=user
        )
        assert clip.pk is not None
        assert clip.exported_by == user

    def test_clip_source_recording_on_delete(self, camera):
        """Test that deleting the source recording sets the clip's source to NULL."""
        recording = Recording.objects.create(camera=camera, recording_type="manual", start_time=timezone.now(), end_time=timezone.now(), object_prefix="rec/", duration_seconds=10)
        clip = Clip.objects.create(camera=camera, source_recording=recording, start_time=timezone.now(), end_time=timezone.now(), object_key="key")
        
        recording.delete()
        clip.refresh_from_db()
        
        assert clip.source_recording is None

    def test_delete_user_sets_exported_by_to_null(self, camera, user):
        """Test that deleting a user sets the clip's exported_by field to NULL."""
        clip = Clip.objects.create(camera=camera, exported_by=user, start_time=timezone.now(), end_time=timezone.now(), object_key="key")
        
        user.delete()
        clip.refresh_from_db()

        assert clip.exported_by is None
