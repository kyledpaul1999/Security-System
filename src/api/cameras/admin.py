from django.contrib import admin
from .models import NvrDevice, Camera, CameraPtzPreset

admin.site.register(NvrDevice)
admin.site.register(Camera)
admin.site.register(CameraPtzPreset)
