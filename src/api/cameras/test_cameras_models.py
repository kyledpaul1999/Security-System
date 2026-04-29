
import pytest
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from .models import NvrDevice, Camera, CameraPtzPreset

@pytest.mark.django_db
class TestNvrDeviceModel:

    def test_create_nvr_device(self):
        """Test creating a NvrDevice instance."""
        device = NvrDevice.objects.create(
            name="Test NVR",
            host="192.168.1.100",
            port=8000,
            username="admin",
        )
        assert device.pk is not None
        assert device.name == "Test NVR"
        assert device.status == "unknown"

    def test_nvr_device_str(self):
        """Test the string representation of NvrDevice."""
        device = NvrDevice(name="Main NVR")
        assert str(device) == "Main NVR"

    def test_host_port_unique_together(self):
        """Test that the host and port combination must be unique."""
        NvrDevice.objects.create(name="NVR1", host="192.168.1.1", port=80)
        with pytest.raises(ValidationError):
            device2 = NvrDevice(name="NVR2", host="192.168.1.1", port=80)
            device2.full_clean()

@pytest.mark.django_db
class TestCameraModel:

    def test_create_camera(self):
        """Test creating a Camera instance."""
        camera = Camera.objects.create(
            name="Test Camera",
            channel_no=1,
        )
        assert camera.pk is not None
        assert camera.name == "Test Camera"
        assert camera.is_enabled is True
        assert camera.health_status == "unknown"

    def test_camera_with_nvr(self):
        """Test creating a camera associated with an NVR."""
        nvr = NvrDevice.objects.create(name="Main NVR", host="192.168.1.101", port=8000)
        camera = Camera.objects.create(
            name="Front Door Camera",
            channel_no=2,
            nvr_device=nvr,
        )
        assert camera.nvr_device == nvr
        assert nvr.cameras.count() == 1

    def test_camera_str(self):
        """Test the string representation of Camera."""
        camera = Camera(name="Lobby Camera")
        assert str(camera) == "Lobby Camera"

    def test_delete_nvr_sets_camera_nvr_to_null(self):
        """Test that deleting an NVR sets the camera's nvr_device to NULL."""
        nvr = NvrDevice.objects.create(name="Lobby NVR", host="192.168.1.102", port=80)
        camera = Camera.objects.create(name="Lobby Cam", channel_no=1, nvr_device=nvr)
        
        nvr.delete()
        camera.refresh_from_db()
        
        assert camera.nvr_device is None

@pytest.mark.django_db
class TestCameraPtzPresetModel:

    def test_create_ptz_preset(self):
        """Test creating a CameraPtzPreset instance."""
        camera = Camera.objects.create(name="Rooftop Camera", channel_no=3)
        preset = CameraPtzPreset.objects.create(
            camera=camera,
            name="Skyline View",
            preset_token="preset1",
        )
        assert preset.pk is not None
        assert preset.camera == camera
        assert camera.ptz_presets.count() == 1

    def test_ptz_preset_str(self):
        """Test the string representation of CameraPtzPreset."""
        camera = Camera(name="Parking Lot")
        preset = CameraPtzPreset(camera=camera, name="Entrance")
        assert str(preset) == "Parking Lot - Entrance"

    def test_delete_camera_cascades_to_presets(self):
        """Test that deleting a camera also deletes its PTZ presets."""
        camera = Camera.objects.create(name="Warehouse Cam", channel_no=4)
        CameraPtzPreset.objects.create(camera=camera, name="Aisle 1", preset_token="p1")
        CameraPtzPreset.objects.create(camera=camera, name="Aisle 2", preset_token="p2")
        
        assert CameraPtzPreset.objects.count() == 2
        camera.delete()
        assert CameraPtzPreset.objects.count() == 0
