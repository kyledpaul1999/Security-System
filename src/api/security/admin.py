from django.contrib import admin
from .models import AuditLog, SystemHealthEvent

admin.site.register(AuditLog)
admin.site.register(SystemHealthEvent)
