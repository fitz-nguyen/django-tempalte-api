import uuid

from django.conf import settings
from django.db import models
from model_utils.models import TimeStampedModel


class DeviceInfo(TimeStampedModel):
    """
    Store device information.
    """

    IOS = "IOS"
    DROID = "DROID"
    PLATFORMS = ((IOS, "iOS"), (DROID, "Android"))

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device_id = models.CharField(max_length=255, null=False, blank=False, unique=True)
    platform = models.CharField(max_length=20, choices=PLATFORMS, null=True, blank=True)
    platform_version = models.CharField(max_length=10, null=True, blank=True)
    blocked = models.BooleanField(default=False, null=False)
    app_version = models.CharField(max_length=10, null=True, blank=True)
    memo = models.CharField(max_length=250, null=True, blank=True, help_text="Internal notes")

    class Meta:
        verbose_name = "Device"
        verbose_name_plural = "Devices"

    def set_platform_str(self, platform_str):
        if platform_str == "ios":
            self.platform = self.IOS
        elif platform_str == "droid":
            self.platform = self.DROID
        else:
            assert False, "platform_str must be ios or droid"

    def __str__(self):
        return "%s, %s, %s" % (
            self.device_id,
            self.platform,
            self.platform_version,
        )


class UserDevice(TimeStampedModel):
    """
    Associate user to device.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    device = models.ForeignKey(DeviceInfo, on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    last_used = models.DateTimeField(blank=True, null=True)
    in_use = models.BooleanField(default=True)
    memo = models.CharField(max_length=250, null=True, blank=True, help_text="Internal notes")

    class Meta:
        unique_together = ("device", "user")
        verbose_name = "User - Device"
        verbose_name_plural = "User - Device(s)"

    def __str__(self):
        return f"{self.user}: {self.device}"
