import uuid

from apps.systems import choices
from apps.systems.choices import STORM_DAMAGE_TIME_UNIT
from django.db import models
from model_utils.models import TimeStampedModel
from s3direct.fields import S3DirectField
from tinymce.models import HTMLField


class PageConfig(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    content = HTMLField(blank=True, null=True)
    type = models.CharField(choices=choices.PAGE_CHOICES, default=choices.LEARN_MORE_WEB, max_length=100)
    published = models.BooleanField(default=True)

    class Meta:
        ordering = ["-created"]
        verbose_name = "Page Content"
        verbose_name_plural = "Page Contents"

    def __str__(self):
        return self.title if self.title else self.id


class NotInterestedReasonConfig(TimeStampedModel):
    value = models.CharField(max_length=100)
    order = models.IntegerField(default=0)


class SaleStatusConfig(TimeStampedModel):
    key = models.CharField(max_length=100, null=True, blank=True)
    value = models.CharField(max_length=100)
    hex_color = models.CharField(max_length=100, null=True, blank=True)
    order = models.IntegerField(default=0)


class HirePredictionConfig(TimeStampedModel):
    key = models.CharField(max_length=100, null=True, blank=True)
    value = models.CharField(max_length=100)
    order = models.IntegerField(default=0)
    hex_color = models.CharField(max_length=100, null=True, blank=True)
    icon_url = models.CharField(max_length=100, null=True, blank=True)


class RoofMaterialConfig(TimeStampedModel):
    key = models.CharField(max_length=100, null=True, blank=True)
    value = models.CharField(max_length=100)
    order = models.IntegerField(default=0)


class HomeSizeConfig(TimeStampedModel):
    key = models.CharField(max_length=30)
    value = models.CharField(max_length=100, null=True, blank=True)
    total_sqft_from = models.IntegerField(null=True, blank=True)  # Min size
    total_sqft_to = models.IntegerField(null=True, blank=True)  # Max size
    description = models.CharField(max_length=255, null=True, blank=True)
    order = models.IntegerField(default=0)


class SystemConfig(TimeStampedModel):
    export_building_permit_count_limit = models.BigIntegerField(default=10000000)
    import_chunk_size = models.IntegerField(default=100000)
    customer_lead_import_limit = models.BigIntegerField(
        default=10000, help_text="Maximum number of leads a customer can import."
    )
    customer_max_lead_file_size = models.BigIntegerField(
        default=10000, help_text="Maximum file size (in bytes) for lead import by a customer."
    )
    csv_example_file = S3DirectField(
        dest="s3_admin_upload",
        null=True,
        blank=True,
        help_text="file name allowed character is a-z, 1-9",
    )
    csv_map_generation_duration = models.BigIntegerField(
        default=1800, help_text="Time duration (in seconds) for generating a lead CSV file"
    )
    reach_valid_distance = models.IntegerField(
        default=10, help_text="Maximum distance (in feet) allowed for validating a reach."
    )
    visit_valid_distance = models.IntegerField(
        default=100, help_text="Maximum distance (in feet) allowed for validating a visit."
    )
    email_footer_url = models.CharField(max_length=1000, null=True, blank=True)
    facebook_page_url = models.CharField(max_length=100, null=True, blank=True)
    instagram_page_url = models.CharField(max_length=100, null=True, blank=True)
    x_page_url = models.CharField(max_length=100, null=True, blank=True)


class StormDamageConfig(TimeStampedModel):
    key = models.CharField(max_length=100)
    unit_value = models.IntegerField(null=True, blank=True)
    value = models.CharField(max_length=100, null=True, blank=True)
    unit = models.CharField(choices=STORM_DAMAGE_TIME_UNIT, default="", max_length=100)
    order = models.IntegerField(default=0)
