from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('identities.urls')),
    path('api/', include('cameras.urls')),

    path('api/', include('recordings.urls')),
    path('api/', include('detections.urls')),
    path('api/', include('automations.urls')),
    path('api/', include('notifications.urls')),
    path('api/', include('security.urls')),
]
