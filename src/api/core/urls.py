from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include([
        path('identities/', include('identities.urls')),
        path('cameras/', include('cameras.urls')),
        path('recordings/', include('recordings.urls')),
        path('detections/', include('detections.urls')),
        path('automations/', include('automations.urls')),
        path('notifications/', include('notifications.urls')),
        path('auditing/', include('auditing.urls')),
        path('security/', include('security.urls')),
    ])),
]
