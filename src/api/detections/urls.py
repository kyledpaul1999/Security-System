from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DetectionEventViewSet

router = DefaultRouter()
router.register(r'events', DetectionEventViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
