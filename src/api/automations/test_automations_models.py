
import pytest
from django.utils import timezone
from identities.models import User
from automations.models import AutomationRule, AutomationRun, AutomationActionRun
from detections.models import DetectionEvent
from cameras.models import Camera

@pytest.fixture
def user():
    return User.objects.create_user(username="testuser", password="password")

@pytest.mark.django_db
class TestAutomationRuleModel:

    def test_create_automation_rule(self, user):
        """Test creating an AutomationRule."""
        rule = AutomationRule.objects.create(
            name="Test Rule",
            trigger_type="event",
            conditions={"field": "confidence", "operator": "gte", "value": 0.9},
            actions=[{"type": "send_email"}],
            created_by=user
        )
        assert rule.pk is not None
        assert rule.name == "Test Rule"
        assert rule.created_by == user

    def test_delete_user_sets_created_by_to_null(self, user):
        """Test that deleting a user sets the rule's created_by field to NULL."""
        rule = AutomationRule.objects.create(name="Test Rule 2", created_by=user, conditions={}, actions={})
        user.delete()
        rule.refresh_from_db()
        assert rule.created_by is None

@pytest.mark.django_db
class TestAutomationRunModels:

    @pytest.fixture
    def rule(self, user):
        return AutomationRule.objects.create(name="Test Rule", created_by=user, conditions={}, actions={})

    def test_create_automation_run(self, rule):
        """Test creating an AutomationRun."""
        run = AutomationRun.objects.create(
            rule=rule,
            matched=True,
            status="success"
        )
        assert run.pk is not None
        assert run.status == "success"

    def test_delete_rule_sets_run_rule_to_null(self, rule):
        """Test that deleting a rule sets the run's rule field to NULL."""
        run = AutomationRun.objects.create(rule=rule, matched=True, status="completed")
        rule.delete()
        run.refresh_from_db()
        assert run.rule is None

    def test_automation_run_can_link_to_detection_event(self, rule):
        """Test that an AutomationRun can be linked to a DetectionEvent via UUID."""
        camera = Camera.objects.create(name="Test Camera", channel_no=1)
        event = DetectionEvent.objects.create(
            camera=camera,
            event_type="person",
            confidence=0.99,
            frame_ts=timezone.now(),
            time=timezone.now()
        )
        run = AutomationRun.objects.create(
            rule=rule,
            detection_event_id=event.id,  # Link by ID
            matched=True,
            status="pending"
        )

        retrieved_run = AutomationRun.objects.get(pk=run.pk)
        assert retrieved_run.detection_event_id == event.id

    def test_create_automation_action_run(self, rule):
        """Test creating an AutomationActionRun."""
        run = AutomationRun.objects.create(rule=rule, matched=True, status="in_progress")
        action_run = AutomationActionRun.objects.create(
            automation_run=run,
            action_type="send_push",
            status="pending"
        )
        assert action_run.pk is not None
        assert run.automationactionrun_set.count() == 1

    def test_delete_automation_run_cascades_to_actions(self, rule):
        """Test that deleting an automation run deletes its action runs."""
        run = AutomationRun.objects.create(rule=rule, matched=True, status="running")
        AutomationActionRun.objects.create(automation_run=run, action_type="start_recording", status="success")
        assert AutomationActionRun.objects.count() == 1
        run.delete()
        assert AutomationActionRun.objects.count() == 0
