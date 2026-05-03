
from django.db import migrations
from django.contrib.auth import get_user_model

def create_initial_data(apps, schema_editor):
    User = get_user_model()
    Role = apps.get_model('identities', 'Role')
    NvrDevice = apps.get_model('cameras', 'NvrDevice')
    Camera = apps.get_model('cameras', 'Camera')
    AutomationRule = apps.get_model('automations', 'AutomationRule')

    # Create Roles
    admin_role, _ = Role.objects.get_or_create(name='admin')
    viewer_role, _ = Role.objects.get_or_create(name='viewer')

    # Create Admin User
    if not User.objects.filter(username='admin').exists():
        admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'password')
        admin_user.roles.add(admin_role)

    # Create NVR Device
    nvr, _ = NvrDevice.objects.get_or_create(
        name='Main NVR',
        host='192.168.1.108',
        port=8000,
        username='admin',
        encrypted_credentials='' # Add encrypted password here
    )

    # Create Camera
    Camera.objects.get_or_create(
        name='Front Door',
        channel_no=1,
        nvr_device=nvr,
        rtsp_main_url='rtsp://user:pass@192.168.1.108:554/Streaming/Channels/101/'
    )

    # Create Automation Rule
    AutomationRule.objects.get_or_create(
        name='Person Detection Alert',
        trigger_event_type='person',
        conditions={'confidence_threshold': 0.9},
        defaults={
            'actions': [{'type': 'send_webhook', 'url': 'http://localhost:8000/webhook-receiver'}]
        }
    )

class Migration(migrations.Migration):

    dependencies = [
        ('identities', '0001_initial'),
        ('cameras', '0001_initial'),
        ('automations', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_data),
    ]
