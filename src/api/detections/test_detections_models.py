
import pytest
from django.utils import timezone
from django.core.exceptions import ValidationError
from cameras.models import Camera
from detections.models import DetectionZone, DetectionEvent, DetectionPolicy

@pytest.fixture
def camera():
    return Camera.objects.create(name="Test Camera", channel_no=1)

@pytest.mark.django_db
class TestDetectionZoneModel:

    def test_create_detection_zone(self, camera):
        """Test creating a DetectionZone with valid polygon data."""
        zone = DetectionZone.objects.create(
            camera=camera,
            name="Porch",
            polygon=[{"x": 0, "y": 0}, {"x": 100, "y": 0}, {"x": 100, "y": 100}, {"x": 0, "y": 100}]
        )
        assert zone.pk is not None
        assert zone.name == "Porch"
        assert camera.detection_zones.count() == 1

    def test_zone_str(self, camera):
        """Test the string representation of DetectionZone."""
        zone = DetectionZone(camera=camera, name="Driveway")
        assert str(zone) == "Test Camera - Driveway"

    def test_delete_camera_cascades_to_zones(self, camera):
        """Test that deleting a camera also deletes its detection zones."""
        DetectionZone.objects.create(camera=camera, name="Zone 1", polygon=[])
        assert DetectionZone.objects.count() == 1
        camera.delete()
        assert DetectionZone.objects.count() == 0

@pytest.mark.django_db
class TestDetectionEventModel:

    def test_create_detection_event(self, camera):
        """Test creating a DetectionEvent."""
        event = DetectionEvent.objects.create(
            camera=camera,
            event_type="person",
            confidence=0.95,
            frame_ts=timezone.now(),
            time=timezone.now()
        )
        assert event.pk is not None
        assert event.confidence == 0.95
        assert camera.detection_events.count() == 1

    def test_event_with_zone(self, camera):
        """Test creating a detection event associated with a zone."""
        zone = DetectionZone.objects.create(camera=camera, name="Garden", polygon=[])
        event = DetectionEvent.objects.create(
            camera=camera, 
            zone=zone, 
            event_type="animal", 
            confidence=0.8, 
            frame_ts=timezone.now(),
            time=timezone.now()
        )
        assert event.zone == zone

@pytest.mark.django_db
class TestDetectionPolicyModel:

    def test_create_policy_for_camera(self, camera):
        """Test creating a detection policy linked to a camera."""
        policy = DetectionPolicy.objects.create(camera=camera, min_confidence=0.8)
        assert policy.pk is not None
        assert policy.min_confidence == 0.8

    def test_confidence_validation(self):
        """Test that min_confidence must be between 0 and 1."""
        policy = DetectionPolicy(min_confidence=1.1)
        with pytest.raises(ValidationError):
            policy.full_clean()  # This will trigger model validation

        policy.min_confidence = -0.1
        with pytest.raises(ValidationError):
            policy.full_clean()
