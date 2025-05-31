import uuid

from django.db import models
from model_utils.models import TimeStampedModel

from apps.core.utils import get_media_url
from apps.uploads.enums import FileState
from apps.users.models import User


class UploadFile(TimeStampedModel):
    FILE_STATES = (
        (FileState.USED, "USED"),
        (FileState.NEW, "NEW"),
        (FileState.DELETED, "DELETED"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(
        choices=FILE_STATES,
        max_length=128,
        default=FileState.NEW,
        blank=True,
        null=True,
    )
    file_path = models.FileField(max_length=128, null=True, blank=True)
    thumbnail_path = models.JSONField(null=True)
    size = models.IntegerField(null=True)
    mime_type = models.CharField(max_length=128, null=True, blank=True)
    storage = models.CharField(max_length=128, null=True, blank=True)
    metadata = models.JSONField(null=True)
    ip_address = models.CharField(max_length=128, null=True, blank=True)
    user = models.ForeignKey(User, related_name="upload_files", on_delete=models.CASCADE, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["file_path"]),
        ]
        verbose_name = "Upload File"
        verbose_name_plural = "Upload Files"

    def is_new(self) -> bool:
        return self.status == FileState.NEW

    def is_used(self) -> bool:
        return self.status == FileState.USED

    def mark_as_used(self):
        self.status = FileState.USED
        self.save()

    def mark_as_deleted(self):
        self.status = FileState.DELETED
        self.save()

    @property
    def url(self):
        if not self.file_path:
            return None
        return get_media_url(self.file_path.name)

    def is_image(self):
        return "image" in str(self.mime_type)
