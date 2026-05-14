from datetime import datetime
from recordings.models import Recording, RecordingSegment, Clip

class RecordingService:
    def start_recording(self, camera, recording_type):
        recording = Recording.create_recording(
            camera=camera,
            recording_type=recording_type,
            start_time=datetime.now(),
            end_time=None,
            object_prefix=f"recordings/{camera.id}/{datetime.now().strftime('%Y/%m/%d/%H')}",
            duration_seconds=0,
            total_size_bytes=0,
        )
        return recording

    def stop_recording(self, recording):
        recording.end_time = datetime.now()
        recording.save()

    def create_clip(self, recording, start_time, end_time):
        clip = Clip.objects.create(
            camera=recording.camera,
            source_recording=recording,
            start_time=start_time,
            end_time=end_time,
            object_key=f"clips/{recording.camera.id}/{datetime.now().strftime('%Y/%m/%d/%H')}/{uuid.uuid4()}.mp4",
        )
        return clip
