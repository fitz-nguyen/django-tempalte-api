import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser, AnonymousUser
from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel

from apps.core.utils import get_media_url, get_storage_path
from apps.users import choices
from apps.users.choices import CREATED_VIA_CHOICES, WEB

AnonymousUser.is_systemuser = False


class User(AbstractUser, TimeStampedModel):
    def avatar_path(self, filename, *args, **kwargs):
        return get_storage_path(filename, "avatar")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    company = models.ForeignKey(
        "Company", on_delete=models.PROTECT, null=True, blank=True, related_name="users", verbose_name="Company"
    )
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=choices.USER_STATUS,
        default=choices.PENDING,
        help_text=_("User approval status"),
    )
    avatar = models.CharField(null=True, blank=True, max_length=1000)  # type: str
    avatar_thumb = models.CharField(null=True, blank=True, max_length=1000)  # type: str
    display_name = models.CharField(
        default="", blank=True, max_length=100
    )  # as we can save metadata which get from gg or here map
    role = models.CharField(_("Role"), max_length=30, choices=choices.USER_ROLES, default=choices.REGULAR)
    profile_complete = models.BooleanField(default=False)
    created_via = models.CharField(max_length=10, choices=CREATED_VIA_CHOICES, default=WEB)
    is_sent_mail_approve_account = models.BooleanField(default=False)
    email_verified = models.BooleanField(_("Email Verified"), default=False)
    notification = models.BooleanField(default=True)
    metadata = models.JSONField(null=True, blank=True)
    is_active = models.BooleanField(
        _("Active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. " "Unselect this instead of deleting accounts."
        ),
    )
    is_systemuser = models.BooleanField(
        _("System User"),
        default=False,
        help_text=_(
            "Designates whether this user is a system user with special permissions."
        ),
    )

    is_staff = models.BooleanField(
        _("StaffAdmin User"),
        default=False,
        help_text=_("Designates whether the user can log into this admin site."),
    )

    is_superuser = models.BooleanField(
        _("Superadmin User"),
        default=False,
        help_text=_(
            "Designates that this user has all permissions without "
            "explicitly assigning them."
        ),
    )

    def __str__(self):
        name = " ".join(filter(None, [self.first_name, self.last_name]))
        return f"{name} - {self.email}" if name else self.email

    @property
    def name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email

    def get_display_name(self):
        if self.display_name:
            return self.display_name
        return self.name

    def impersonate_user(self):
        if not self.is_regular_user() or self.status != choices.APPROVED:
            return ""
        return format_html(
            '<a href="{}" target="_blank">Impersonate</a>',
            reverse("impersonate_user", args=[self.id]),
        )

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email

        if not self.display_name or self.display_name != f"{self.first_name} {self.last_name}":
            self.display_name = f"{self.first_name} {self.last_name}"

        super().save(*args, **kwargs)

    def get_avatar(self):
        if self.avatar_thumb:
            return get_media_url(self.avatar_thumb)
        elif self.avatar:
            return get_media_url(self.avatar)
        return None

    def is_admin(self):
        return self.role == choices.ADMIN

    def is_sales_representative(self):
        return self.role == choices.SALE

    def is_regular_user(self):
        return self.role == choices.REGULAR


class Admin(User):
    class Meta:
        proxy = True
        verbose_name_plural = "Admins"

    def save(self, *args, **kwargs):
        self.role = choices.ADMIN
        super().save(*args, **kwargs)

    @classmethod
    def get_queryset(cls):
        return super().get_queryset().filter(role=choices.ADMIN)


class SalesRepresentative(User):
    class Meta:
        proxy = True
        verbose_name_plural = "Sales Representatives"

    def save(self, *args, **kwargs):
        self.role = choices.SALE
        super().save(*args, **kwargs)

    @classmethod
    def get_queryset(cls):
        return super().get_queryset().filter(role=choices.SALE)


class RegularUser(User):
    class Meta:
        proxy = True
        verbose_name_plural = "Regular Users"

    def save(self, *args, **kwargs):
        self.role = choices.REGULAR
        super().save(*args, **kwargs)

    @classmethod
    def get_queryset(cls):
        return super().get_queryset().filter(role=choices.REGULAR)


class PendingUser(User):
    class Meta:
        proxy = True
        verbose_name_plural = "Pending Users"

    @classmethod
    def get_queryset(cls):
        return super().get_queryset().filter(status=choices.PENDING)


class ApproveUser(User):
    class Meta:
        proxy = True
        verbose_name_plural = "Approved Users"

    @classmethod
    def get_queryset(cls):
        return super().get_queryset().filter(status=choices.APPROVED)


class ResetPasswordOTP(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    otp = models.CharField(max_length=6, null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["user", "is_verified"]),
        ]
        verbose_name = "Reset Password OTP"
        verbose_name_plural = "Reset Password OTPs"

    def __str__(self):
        return f"{self.created}: {self.user} - {self.otp}"


class Company(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    business_name = models.CharField(_("Business Name"), max_length=255, unique=True)
    business_address = models.JSONField(_("Business Address"), default=dict)  # Changed from JSONField to CharField
    region_served = models.JSONField(
        _("Region Served"), default=list
    )  # Changed to store list of dicts with zip, city, state
    dashboard_data_uri = models.CharField(max_length=200, null=True)
    is_active = models.BooleanField(_("Active Status"), default=True)
    is_csv_processing = models.BooleanField(_("CSV Processing Status"), default=False)
    last_update_csv_time = models.DateTimeField(_("Last CSV Update Time"), auto_now=True)
    contact_firstname = models.CharField(default="", blank=True, max_length=100)
    contact_lastname = models.CharField(default="", blank=True, max_length=100)
    contact_phone_e164 = models.CharField(max_length=20, null=True, blank=True)
    contact_phone_number = models.CharField(max_length=20, null=True, blank=True)
    contact_phone_country_code = models.CharField(max_length=10, null=True, blank=True)
    metadata = models.JSONField(_("Additional Information"), null=True, blank=True)
    centre_point = models.JSONField(_("Centre Point"), null=True, blank=True)

    class Meta:
        verbose_name = _("Company")
        verbose_name_plural = _("Companies")

    def __str__(self):
        return self.business_name

    def zips(self):
        if self.region_served:
            return [region["zip"] for region in self.region_served]
        return []


class SaleLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                             related_name="sale_logs", verbose_name=_("User"))
    lead_id = models.CharField(max_length=50, null=True)
    event = models.CharField(max_length=100)
    detail = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Sale Log")
        verbose_name_plural = _("Sale Logs")
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.user.email} - {self.event} - {self.timestamp}"
