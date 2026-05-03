from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NvrDeviceViewSet, CameraViewSet, CameraPtzPresetViewSet

router = DefaultRouter()
router.register(r'nvrs', NvrDeviceViewSet)
router.register(r'cameras', CameraViewSet)
router.register(r'ptz-presets', CameraPtzPresetViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
