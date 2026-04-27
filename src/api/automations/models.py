from django.db import models
import uuid
from identities.models import User

class AutomationRule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    trigger_type = models.CharField(max_length=50)
    trigger_event_type = models.CharField(max_length=100, blank=True, null=True)
    conditions = models.JSONField()
    actions = models.JSONField()
    cooldown_seconds = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class AutomationRun(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rule = models.ForeignKey(AutomationRule, on_delete=models.SET_NULL, blank=True, null=True)
    source_event_type = models.CharField(max_length=100, blank=True, null=True)
    source_event_id = models.UUIDField(blank=True, null=True)
    matched = models.BooleanField()
    status = models.CharField(max_length=50)
    result = models.JSONField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class AutomationActionRun(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    automation_run = models.ForeignKey(AutomationRun, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=100)
    status = models.CharField(max_length=50)
    attempts = models.IntegerField(default=0)
    result = models.JSONField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
