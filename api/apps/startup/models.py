import uuid

from django.db import models
from model_utils.models import TimeStampedModel

from apps.startup import choices


class AppVersion(TimeStampedModel):
    """
    Store app minimal version and current version
    """

    IOS = "IOS"
    DROID = "DROID"
    PLATFORMS = ((IOS, "iOS"), (DROID, "Android"))

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    minimal_version = models.CharField(max_length=10, default="1.0.0")
    current_version = models.CharField(max_length=10, default="1.0.0")
    platform = models.CharField(max_length=20, choices=PLATFORMS, null=True, blank=True)
    app_store_url = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "App Version"
        verbose_name_plural = "App Versions"

    def __str__(self):
        return "%s - %s" % (self.minimal_version, self.current_version)

    @classmethod
    def get_app_version(cls, platform):

        if platform not in dict(cls.PLATFORMS):
            return None

        version = AppVersion.objects.filter(platform=platform).first()
        if version is None:
            version = AppVersion.objects.create(
                minimal_version="1.0.0",
                current_version="1.0.0",
                platform=platform,
            )
        return version


class Message(TimeStampedModel):
    """
    Store messages for start up check
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=100, blank=True, null=True)
    message = models.CharField(max_length=250, blank=True, null=True)
    icon = models.CharField(max_length=250, blank=True, null=True)
    background = models.CharField(max_length=250, blank=True, null=True)
    type = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        choices=choices.MESSAGE_STARTUP_CHOICES,
        default=choices.MESSAGE_UPDATE_APP,
    )

    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"

    def __str__(self):
        return f"{self.title} - {self.message} - {self.icon} - {self.background}"

    @classmethod
    def get_update_app_message(cls):
        return Message.objects.filter(type=choices.MESSAGE_UPDATE_APP).first()
