from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include([
        path('identities/', include('src.api.identities.urls')),
        path('cameras/', include('src.api.cameras.urls')),
        path('recordings/', include('src.api.recordings.urls')),
        path('detections/', include('src.api.detections.urls')),
        path('automations/', include('src.api.automations.urls')),
        path('notifications/', include('src.api.notifications.urls')),
        path('security/', include('src.api.security.urls')),
    ])),
]
