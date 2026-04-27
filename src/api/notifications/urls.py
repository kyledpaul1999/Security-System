from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationRuleViewSet, NotificationViewSet

router = DefaultRouter()
router.register(r'rules', NotificationRuleViewSet)
router.register(r'notifications', NotificationViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
