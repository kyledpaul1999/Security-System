from django.contrib import admin
from .models import AutomationRule, AutomationRun, AutomationActionRun

admin.site.register(AutomationRule)
admin.site.register(AutomationRun)
admin.site.register(AutomationActionRun)
