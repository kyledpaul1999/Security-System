
import pytest
from unittest.mock import patch, MagicMock
from src.event_handler.main import route_alert
from src.api.automations.models import AutomationRule, AutomationAction

@pytest.fixture
def mock_rule():
    rule = MagicMock(spec=AutomationRule)
    rule.name = 'Test Rule'
    rule.conditions = {'confidence_threshold': 0.9}
    
    action = MagicMock(spec=AutomationAction)
    action.action_type = 'send_webhook'
    action.action_params = {'url': 'http://test.webhook.url'}
    
    rule.actions.all.return_value = [action]
    return rule

@pytest.mark.django_db
@patch('src.event_handler.main.send_webhook')
@patch('src.event_handler.main.AutomationRule.objects')
def test_route_alert_sends_webhook(mock_rules_objects, mock_send_webhook, mock_rule):
    """
    Test that route_alert correctly evaluates a rule and calls the send_webhook action.
    """
    mock_rules_objects.filter.return_value = [mock_rule]
    
    event_data = {
        'label': 'person',
        'confidence': 0.95,
        'camera-id': 'test-cam'
    }
    
    route_alert(event_data)
    
    mock_send_webhook.assert_called_once_with('http://test.webhook.url', event_data)
