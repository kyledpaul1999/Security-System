from django.contrib import admin
from .models import NotificationRule, Notification

admin.site.register(NotificationRule)
admin.site.register(Notification)
