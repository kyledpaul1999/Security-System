from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AuditLogViewSet, SystemHealthEventViewSet

router = DefaultRouter()
router.register(r'auditlogs', AuditLogViewSet)
router.register(r'systemhealthevents', SystemHealthEventViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
