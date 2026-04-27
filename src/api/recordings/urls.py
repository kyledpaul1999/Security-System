from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RecordingViewSet, LiveStreamViewSet

router = DefaultRouter()
router.register(r'recordings', RecordingViewSet)
router.register(r'livestreams', LiveStreamViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
