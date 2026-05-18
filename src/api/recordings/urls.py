from rest_framework.routers import DefaultRouter
from recordings.views import RecordingViewSet, ClipViewSet, LiveStreamStatusViewSet

router = DefaultRouter()
router.register(r'recordings', RecordingViewSet)
router.register(r'clips', ClipViewSet)
router.register(r'livestream-status', LiveStreamStatusViewSet, basename='livestream-status')

urlpatterns = router.urls
