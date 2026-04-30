
import pytest
from django.utils import timezone
from cameras.models import Camera
from identities.models import User
from detections.models import DetectionZone, DetectionEvent
from notifications.models import NotificationRule, Notification

@pytest.fixture
def user():
    return User.objects.create_user(username="testuser", password="password")

@pytest.fixture
def camera():
    return Camera.objects.create(name="Test Camera", channel_no=1)

@pytest.mark.django_db
class TestNotificationRuleModel:

    def test_create_notification_rule(self, user, camera):
        """Test creating a NotificationRule."""
        rule = NotificationRule.objects.create(
            user=user,
            camera=camera,
            event_type="person_detected",
            delivery_channel="email",
            destination="test@example.com"
        )
        assert rule.pk is not None
        assert rule.user == user

    def test_delete_user_cascades_to_rules(self, user, camera):
        """Test that deleting a user also deletes their notification rules."""
        NotificationRule.objects.create(user=user, camera=camera, event_type="connection_lost", delivery_channel="webhook", destination="http://hooks.test")
        assert NotificationRule.objects.count() == 1
        user.delete()
        assert NotificationRule.objects.count() == 0

    def test_delete_camera_cascades_to_rules(self, user, camera):
        """Test that deleting a camera also deletes its related notification rules."""
        NotificationRule.objects.create(user=user, camera=camera, event_type="motion", delivery_channel="email", destination="a@b.com")
        assert NotificationRule.objects.count() == 1
        camera.delete()
        assert NotificationRule.objects.count() == 0

@pytest.mark.django_db
class TestNotificationModel:

    @pytest.fixture
    def rule(self, user, camera):
        return NotificationRule.objects.create(user=user, camera=camera, event_type="person", delivery_channel="email", destination="t@test.com")

    def test_create_notification(self, rule):
        """Test creating a Notification."""
        notification = Notification.objects.create(
            rule=rule,
            delivery_channel="email",
            destination="t@test.com",
            status="pending"
        )
        assert notification.pk is not None
        assert notification.status == "pending"

    def test_notification_rule_on_delete(self, rule):
        """Test that deleting a rule sets the notification's rule field to NULL."""
        notification = Notification.objects.create(rule=rule, delivery_channel="email", destination="t@test.com", status="sent")
        
        rule.delete()
        notification.refresh_from_db()

        assert notification.rule is None

    def test_notification_can_link_to_detection_event(self, rule, camera):
        """Test that a Notification can be linked to a DetectionEvent via UUID."""
        event = DetectionEvent.objects.create(
            camera=camera,
            event_type="person",
            confidence=0.99,
            frame_ts=timezone.now(),
            time=timezone.now()
        )
        notification = Notification.objects.create(
            rule=rule,
            detection_event_id=event.id,  # Link by ID
            delivery_channel="email",
            destination="t@test.com",
            status="pending"
        )

        retrieved_notification = Notification.objects.get(pk=notification.pk)
        assert retrieved_notification.detection_event_id == event.id

    def test_detection_event_on_delete(self, rule, camera):
        """Test that deleting a detection event sets the notification's event field to NULL."""
        event = DetectionEvent.objects.create(camera=camera, event_type="person", confidence=0.9, frame_ts=timezone.now(), time=timezone.now())
        notification = Notification.objects.create(rule=rule, detection_event_id=event.id, delivery_channel="email", destination="t@test.com", status="sent")

        # This test no longer applies in the same way, as there is no cascade or SET_NULL.
        # Instead, we are just testing that the ID is stored.
        # The relationship is now logical, not enforced by the database.
        event.delete()
        notification.refresh_from_db()

        # The ID should still be there.
        assert notification.detection_event_id is not None
