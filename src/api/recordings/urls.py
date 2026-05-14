from rest_framework.routers import DefaultRouter
from recordings.views import RecordingViewSet, ClipViewSet

router = DefaultRouter()
router.register(r'recordings', RecordingViewSet)
router.register(r'clips', ClipViewSet)

urlpatterns = router.urls
