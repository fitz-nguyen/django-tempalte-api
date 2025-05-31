from django.db import models
from model_utils.models import TimeStampedModel


class USLocationInfo(TimeStampedModel):
    state = models.CharField(max_length=255, blank=True, null=True)
    state_abbr = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    zipcode_type = models.CharField(max_length=255, blank=True, null=True)
    county = models.CharField(max_length=255, blank=True, null=True)
    zipcode = models.IntegerField(blank=True, null=True)

    class Meta:
        indexes = [
            models.Index(fields=["state"]),
            models.Index(fields=["city"]),
            models.Index(fields=["zipcode"]),
        ]
        verbose_name = "US Location Info"
        verbose_name_plural = "US Location Info"

    def __str__(self):
        return f"{self.state}"
