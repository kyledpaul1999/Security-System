
import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from src.api.cameras.models import Camera, NvrDevice

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def authenticated_client(api_client):
    user = User.objects.create_user(username='testuser', password='password')
    api_client.force_authenticate(user=user)
    return api_client

@pytest.mark.django_db
class TestCameraAPI:

    def test_list_cameras(self, authenticated_client):
        """Test listing all cameras."""
        Camera.objects.create(name="Test Camera 1", channel_no=1)
        Camera.objects.create(name="Test Camera 2", channel_no=2)
        
        response = authenticated_client.get('/cameras/')
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_create_camera(self, authenticated_client):
        """Test creating a new camera."""
        data = {
            'name': 'New Camera',
            'channel_no': 3
        }
        
        response = authenticated_client.post('/cameras/', data)
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Camera.objects.count() == 1
        assert Camera.objects.get().name == 'New Camera'

    def test_retrieve_camera(self, authenticated_client):
        """Test retrieving a single camera."""
        camera = Camera.objects.create(name="Test Camera", channel_no=1)
        
        response = authenticated_client.get(f'/cameras/{camera.id}/')
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == 'Test Camera'

    def test_update_camera(self, authenticated_client):
        """Test updating a camera's details."""
        camera = Camera.objects.create(name="Old Name", channel_no=1)
        data = {'name': 'New Name'}
        
        response = authenticated_client.patch(f'/cameras/{camera.id}/', data)
        
        assert response.status_code == status.HTTP_200_OK
        camera.refresh_from_db()
        assert camera.name == 'New Name'

    def test_delete_camera(self, authenticated_client):
        """Test deleting a camera."""
        camera = Camera.objects.create(name="Test Camera", channel_no=1)
        
        response = authenticated_client.delete(f'/cameras/{camera.id}/')
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Camera.objects.count() == 0
