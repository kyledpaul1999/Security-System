import os
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage
from django.core.files.storage import FileSystemStorage

class LocalStorage(FileSystemStorage):
    """A wrapper around the default FileSystemStorage to make it compatible with the storage backend selection."""
    pass

class MinioStorage(S3Boto3Storage):
    """A wrapper around the S3Boto3Storage to configure it for MinIO."""
    def __init__(self, **kwargs):
        kwargs['endpoint_url'] = settings.MINIO_ENDPOINT
        kwargs['access_key'] = settings.MINIO_ACCESS_KEY
        kwargs['secret_key'] = settings.MINIO_SECRET_KEY
        super().__init__(**kwargs)

def get_storage_backend():
    """
    A factory function that returns the configured storage backend.
    The selection is based on the STORAGE_BACKEND environment variable.
    """
    storage_backend = os.getenv('STORAGE_BACKEND', 'local')
    if storage_backend == 'minio':
        return MinioStorage()
    else:
        return LocalStorage()
