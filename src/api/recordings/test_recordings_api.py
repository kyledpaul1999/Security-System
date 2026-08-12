
import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from django.utils import timezone
from cameras.models import Camera
from recordings.models import Recording

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def authenticated_client(api_client):
    user = User.objects.create_user(username='testuser', password='password')
    api_client.force_authenticate(user=user)
    return api_client

@pytest.fixture
def camera_fixture():
    return Camera.objects.create(name="Test Camera", channel_no=1)

@pytest.mark.django_db
class TestRecordingAPI:

    def test_list_recordings(self, authenticated_client, camera_fixture):
        """Test listing all recordings."""
        Recording.objects.create(camera=camera_fixture, recording_type="manual", start_time=timezone.now(), end_time=timezone.now(), object_prefix="rec/1", duration_seconds=10)
        Recording.objects.create(camera=camera_fixture, recording_type="motion", start_time=timezone.now(), end_time=timezone.now(), object_prefix="rec/2", duration_seconds=20)
        
        response = authenticated_client.get('/recordings/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_create_recording(self, authenticated_client, camera_fixture):
        """Test creating a new recording."""
        data = {
            'camera': camera_fixture.id,
            'recording_type': 'manual',
            'start_time': timezone.now(),
            'end_time': timezone.now() + timezone.timedelta(minutes=5),
            'object_prefix': 'rec/new/',
            'duration_seconds': 300
        }
        
        response = authenticated_client.post('/recordings/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Recording.objects.count() == 1
        assert Recording.objects.get().recording_type == 'manual'

    def test_retrieve_recording(self, authenticated_client, camera_fixture):
        """Test retrieving a single recording."""
        recording = Recording.objects.create(camera=camera_fixture, recording_type="scheduled", start_time=timezone.now(), end_time=timezone.now(), object_prefix="rec/3", duration_seconds=60)
        
        response = authenticated_client.get(f'/recordings/{recording.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['recording_type'] == 'scheduled'

    def test_update_recording(self, authenticated_client, camera_fixture):
        """Test updating a recording's details."""
        recording = Recording.objects.create(camera=camera_fixture, recording_type="continuous", start_time=timezone.now(), end_time=timezone.now(), object_prefix="rec/4", duration_seconds=120)
        data = {'duration_seconds': 180}
        
        response = authenticated_client.patch(f'/recordings/{recording.id}/', data)
        
        assert response.status_code == status.HTTP_200_OK
        recording.refresh_from_db()
        assert recording.duration_seconds == 180

    def test_delete_recording(self, authenticated_client, camera_fixture):
        """Test deleting a recording."""
        recording = Recording.objects.create(camera=camera_fixture, recording_type="manual", start_time=timezone.now(), end_time=timezone.now(), object_prefix="rec/5", duration_seconds=10)
        
        response = authenticated_client.delete(f'/recordings/{recording.id}/')
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Recording.objects.count() == 0
