from django.contrib import admin
from .models import Recording, RecordingSegment, Clip, LiveStream

admin.site.register(Recording)
admin.site.register(RecordingSegment)
admin.site.register(Clip)
admin.site.register(LiveStream)
