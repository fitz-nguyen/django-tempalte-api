import uuid
from typing import Optional

from django.conf import settings
from django.db import models
from model_utils.models import SoftDeletableModel, TimeStampedModel

from apps.core import utils
from apps.notification import choices


class Message(TimeStampedModel, SoftDeletableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    verb = models.CharField(max_length=100)

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        related_name="actor",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="receiver",
        on_delete=models.CASCADE,
    )

    topic = models.CharField(max_length=100, null=True, blank=True)
    title = models.CharField(max_length=250, null=True, blank=True)
    content = models.CharField(max_length=250, null=True, blank=True)
    template = models.CharField(max_length=250, null=True, blank=True, help_text="Message template")
    status = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        choices=choices.MESSAGE_STATUS_CHOICES,
        default=choices.MESSAGE_STATUS_QUEUED,
    )
    payload = models.JSONField(null=True, blank=True)
    sent_date = models.DateTimeField(null=True, blank=True)
    read = models.BooleanField(default=False)
    visible = models.BooleanField(default=True, help_text="Visible to user?")
    memo = models.CharField(max_length=250, null=True, blank=True, help_text="Internal Notes")
    meta = models.JSONField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["created"]),
            models.Index(fields=["user", "visible", "is_removed"]),
        ]

        verbose_name = "Message"
        verbose_name_plural = "Messages"

    def __str__(self):
        return self.content

    def is_queued(self) -> bool:
        return self.status == choices.MESSAGE_STATUS_QUEUED

    def mark_as_read(self):
        self.read = True
        self.save()

    def mark_as_sent(self):
        self.status = choices.MESSAGE_STATUS_SENT
        self.sent_date = utils.get_utc_now()
        self.save()

    def mark_as_failed(self, error: Optional[str] = None):
        self.status = choices.MESSAGE_STATUS_FAILED
        self.sent_date = utils.get_utc_now()
        if error is not None:
            self.memo = error
        self.save()

    def mark_as_cancelled(self, message: Optional[str] = None):
        self.status = choices.MESSAGE_STATUS_CANCELLED
        if message is not None:
            self.memo = message
        self.save()

    def mark_as_skipped(self, message: Optional[str] = None):
        self.status = choices.MESSAGE_STATUS_SKIPPED
        if message is not None:
            self.memo = message
        self.save()
