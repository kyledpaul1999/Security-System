from django.contrib import admin
from .models import DetectionZone, DetectionPolicy, DetectionEvent

admin.site.register(DetectionZone)
admin.site.register(DetectionPolicy)
admin.site.register(DetectionEvent)
