from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AutomationRuleViewSet, AutomationRunViewSet, AutomationActionRunViewSet

router = DefaultRouter()
router.register(r'rules', AutomationRuleViewSet)
router.register(r'runs', AutomationRunViewSet)
router.register(r'actions', AutomationActionRunViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
