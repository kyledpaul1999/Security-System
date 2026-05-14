from django.core.management.base import BaseCommand
from datetime import datetime, timedelta
from recordings.models import Recording, RetentionPolicy

class Command(BaseCommand):
    help = 'Enforces retention policies for recordings'

    def handle(self, *args, **options):
        for policy in RetentionPolicy.objects.all():
            cutoff = datetime.now() - timedelta(days=policy.retain_for_days)
            recordings_to_delete = Recording.objects.filter(
                camera__retention_policy=policy,
                start_time__lt=cutoff
            )
            for recording in recordings_to_delete:
                # TODO: Delete the actual video files from storage
                self.stdout.write(self.style.SUCCESS(f'Deleting recording {recording.id}'))
                recording.delete()
