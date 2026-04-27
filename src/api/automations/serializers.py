from rest_framework import serializers
from .models import AutomationRule, AutomationRun, AutomationActionRun

class AutomationRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutomationRule
        fields = '__all__'

class AutomationRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutomationRun
        fields = '__all__'

class AutomationActionRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutomationActionRun
        fields = '__all__'
