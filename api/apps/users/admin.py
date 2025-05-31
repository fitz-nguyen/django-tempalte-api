from allauth.account.models import EmailAddress, EmailConfirmation
from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_celery_beat.models import ClockedSchedule, CrontabSchedule, IntervalSchedule, PeriodicTask, SolarSchedule
from oauth2_provider.models import AccessToken, Application, Grant, IDToken, RefreshToken
from rangefilter.filters import DateRangeFilter

from apps.core.admin import StaffAdmin, SystemAdmin
from apps.core.component import DropdownFilter, DropdownFilterForeignKey
from apps.users import choices
from apps.users.forms import (
    AdminUserCreationForm,
    CompanyAdminForm,
    CustomUserChangeForm,
    CustomUserCreationForm,
    RegularUserCreationForm,
    SalesRepresentativeCreationForm,
)
from apps.users.models import (
    Admin,
    ApproveUser,
    Company,
    PendingUser,
    RegularUser,
    ResetPasswordOTP,
    SaleLog,
    SalesRepresentative,
    User,
)
from apps.users_auth.services import send_under_review_mail


class CustomNotViewAdmin(StaffAdmin):
    def has_module_permission(self, request):
        if request.user.is_superuser:
            return True
        else:
            return False


@admin.register(Company)
class CompanyAdmin(StaffAdmin):
    form = CompanyAdminForm
    list_display = ("business_name", "is_active", "is_csv_processing", "dashboard_data_uri", "created", "modified")
    list_filter = ("is_active", "is_csv_processing")
    search_fields = ("business_name",)
    readonly_fields = (
        "id",
        "created",
        "modified",
        "contact_phone_e164",
        "business_address",
        "is_csv_processing",
        "dashboard_data_uri",
    )
    fieldsets = (
        (None, {"fields": ("business_name",)}),
        (
            _("Business Address"),
            {
                "fields": (
                    "business_address",
                    "label",
                    "city",
                    "county",
                    "postal_code",
                    "state",
                    "state_code",
                    "country_name",
                    "country_code",
                    "is_csv_processing",
                    "dashboard_data_uri",
                ),
            },
        ),
        (_("Region Information"), {"fields": ("region_data",)}),
        (
            _("Contact Information"),
            {
                "fields": (
                    "contact_firstname",
                    "contact_lastname",
                    "contact_phone_number",
                    "contact_phone_country_code",
                    "contact_phone_e164",
                )
            },
        ),
        (_("Status"), {"fields": ("is_active",)}),
        (_("Additional Information"), {"fields": ("metadata",)}),
        (_("System Fields"), {"fields": ("id", "created", "modified"), "classes": ("collapse",)}),
    )
    ordering = ("-created", "business_name")

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("users")

    def get_readonly_fields(self, request, obj=None):
        if obj:  # Editing an existing object
            return self.readonly_fields + ("business_name",)  # Make business_name readonly when editing
        return self.readonly_fields

    def clean_business_name(self):
        business_name = self.cleaned_data.get("business_name")
        if business_name:
            # Check for existing company with same business name (case-insensitive)
            existing_company = (
                Company.objects.filter(business_name__iexact=business_name)
                .exclude(id=self.instance.id if self.instance else None)
                .first()
            )

            if existing_company:
                raise ValidationError(_("A company with this business name already exists."))
        return business_name

    def save_model(self, request, obj, form, change):
        # Get current zips if this is an existing company
        old_zips = []
        if change and obj.pk:
            old_company = Company.objects.get(pk=obj.pk)
            old_zips = old_company.zips()

        # Ensure contact_phone_e164 is set correctly
        if obj.contact_phone_number and obj.contact_phone_country_code:
            obj.contact_phone_e164 = obj.contact_phone_country_code + obj.contact_phone_number

        # Validate business name uniqueness
        if not change:  # Only check on creation
            if Company.objects.filter(business_name__iexact=obj.business_name).exists():
                raise ValidationError(_("A company with this business name already exists."))

        super().save_model(request, obj, form, change)


admin.site.unregister(EmailAddress)
admin.site.unregister(EmailConfirmation)


class CustomAuthUserAdmin(AuthUserAdmin, StaffAdmin):
    def save_model(self, request, obj, form, change):
        obj.from_admin_site = True
        super().save_model(request, obj, form, change)


@admin.register(EmailAddress)
class EmailAddressAdmin(SystemAdmin):
    list_display = ("email", "user", "primary", "verified")
    list_filter = ("primary", "verified")
    search_fields = ["email"]
    raw_id_fields = ("user",)

    def has_delete_permission(self, request, obj=None):
        return True


@admin.register(EmailConfirmation)
class EmailConfirmationAdmin(SystemAdmin):
    def has_delete_permission(self, request, obj=None):
        return True


class CompanyDropdownFilter(DropdownFilterForeignKey):
    def field_admin_ordering(self, field, request, model_admin):
        return ("business_name",)


class BaseUserAdmin(CustomAuthUserAdmin):
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("company", "role", "first_name", "last_name", "email", "password1", "password2"),
            },
        ),
    )
    raw_id_fields = ["company"]
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    fieldsets = (
        (None, {"fields": ("email", "password", "company")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "avatar",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "status",
                    "role",
                    "email_verified",
                    "notification",
                    "is_active",
                    "is_systemuser",
                    "is_superuser",
                    "is_staff",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined", "modified")}),
    )
    list_display = (
        "email",
        "first_name",
        "last_name",
        "company",
        "role",
        "status",
        "is_active",
        "email_verified",
        "date_joined",
        "impersonate_user",
    )
    readonly_fields = ("last_login", "is_staff", "date_joined", "modified")
    search_fields = ("email", "first_name", "last_name", "id")
    ordering = ("-date_joined",)
    list_filter = (
        ("company", CompanyDropdownFilter),
        ("role", DropdownFilter),
        ("status", DropdownFilter),
        ("is_active", DropdownFilter),
        ("email_verified", DropdownFilter),
    )
    list_per_page = 50

    def get_readonly_fields(self, request, obj=None):
        readonly = self.readonly_fields

        # If editing an existing user who is both superuser and staff
        if obj and (obj.is_superuser or obj.is_staff):
            # Add 'company' to readonly fields
            readonly = readonly + ('company',)

        if obj:
            if "role" not in readonly:
                readonly = readonly + ('role',)

        return readonly

    def has_delete_permission(self, request, obj=None):
        # If no object is provided, check if user has delete permission in general
        if not obj:
            return super().has_delete_permission(request, obj)

        # If the user to be deleted is a superuser and the current user is not a superuser
        if obj.is_superuser and not request.user.is_superuser:
            return False  # Hide delete button

        return super().has_delete_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        # If no object is provided, check if user has change permission in general
        if not obj:
            return super().has_change_permission(request, obj)

        # Non-superusers cannot edit superusers
        if obj.is_superuser and not request.user.is_superuser:
            return False

        return super().has_change_permission(request, obj)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        """Override to add the impersonate button to the context."""
        extra_context = extra_context or {}

        # Get the user object
        user_obj = self.get_object(request, object_id)

        # Only add impersonate button for regular users with approved status
        if user_obj and user_obj.is_regular_user() and user_obj.status == choices.APPROVED:
            impersonate_url = reverse("impersonate_user", args=[object_id])
            extra_context["impersonate_url"] = impersonate_url

        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def response_change(self, request, obj):
        if hasattr(request, "_systemuser_requires_superuser"):
            messages.error(request, _("System user status can only be granted to superusers."))
            return self.response_post_save_change(request, obj)

        if hasattr(request, "_changed_data") and not request.user.is_superuser:
            if "is_superuser" in request._changed_data:
                messages.error(request, _("You don't have permission to change superuser status."))
                return self.response_post_save_change(request, obj)

            if "is_systemuser" in request._changed_data:
                messages.error(request, _("You don't have permission to change systemuser status."))
                return self.response_post_save_change(request, obj)

        return super().response_change(request, obj)

    def save_model(self, request, obj, form, change):
        # Check if status has changed to APPROVED
        if change and "status" in form.changed_data:
            old_obj = self.model.objects.get(pk=obj.pk)
            if old_obj.status != choices.APPROVED and obj.status == choices.APPROVED:
                # Send email when status changes to APPROVED
                send_under_review_mail(obj.email)

        # Check if protected fields have been changed
        if change and not request.user.is_superuser:
            # Check is_superuser change
            if "is_superuser" in form.changed_data:
                obj.is_superuser = self.model.objects.get(pk=obj.pk).is_superuser
                setattr(request, "_changed_data", form.changed_data)

            # Check is_systemuser change
            if "is_systemuser" in form.changed_data:
                obj.is_systemuser = self.model.objects.get(pk=obj.pk).is_systemuser
                setattr(request, "_changed_data", form.changed_data)

        # Ensure is_systemuser can only be True if the user is a superuser
        if obj.is_systemuser and not obj.is_superuser:
            obj.is_systemuser = False
            # Mark this as a systemuser-superuser validation issue
            setattr(request, "_systemuser_requires_superuser", True)

        # Handle is_staff based on role
        if "role" in form.changed_data or not change:
            if obj.role == choices.ADMIN:
                obj.is_staff = True
            else:
                # If changing from Admin to another role, set is_staff to False
                # unless explicitly set to True in the form
                if not change or (change and "is_staff" not in form.changed_data):
                    obj.is_staff = False

        obj.from_admin_site = True
        super().save_model(request, obj, form, change)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('company')


class UserAdmin(BaseUserAdmin):
    pass


@admin.register(Admin)
class AdminUserAdmin(BaseUserAdmin):
    add_form = AdminUserCreationForm
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("role", "first_name", "last_name", "email", "password1", "password2"),
            },
        ),
    )
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "avatar",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "status",
                    "role",
                    "email_verified",
                    "notification",
                    "is_active",
                    "is_systemuser",
                    "is_superuser",
                    "is_staff",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined", "modified")}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).filter(role=choices.ADMIN)

    def save_model(self, request, obj, form, change):
        # Ensure role is set to Admin
        obj.role = choices.ADMIN

        # Call the parent class's save_model which will handle is_staff and is_superuser validation
        super().save_model(request, obj, form, change)


@admin.register(SalesRepresentative)
class SalesRepresentativeAdmin(BaseUserAdmin):
    add_form = SalesRepresentativeCreationForm

    def get_queryset(self, request):
        return super().get_queryset(request).filter(role=choices.SALE)

    def save_model(self, request, obj, form, change):
        # Ensure role is set to Sales Representative
        obj.role = choices.SALE

        # Call the parent class's save_model which will handle is_staff and is_superuser validation
        super().save_model(request, obj, form, change)


@admin.register(RegularUser)
class RegularUserAdmin(BaseUserAdmin):
    add_form = RegularUserCreationForm

    def get_queryset(self, request):
        return super().get_queryset(request).filter(role=choices.REGULAR)

    def save_model(self, request, obj, form, change):
        # Ensure role is set to Regular
        obj.role = choices.REGULAR

        # Call the parent class's save_model which will handle is_staff and is_superuser validation
        super().save_model(request, obj, form, change)


@admin.register(PendingUser)
class PendingUserAdmin(BaseUserAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(status=choices.PENDING)

    def has_add_permission(self, request):
        return False


@admin.register(ApproveUser)
class ApproveUserAdmin(BaseUserAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request).filter(status=choices.APPROVED)

    def has_add_permission(self, request):
        return False


@admin.register(ResetPasswordOTP)
class ResetPasswordOTPAdmin(StaffAdmin):
    actions = None
    list_display_links = None

    list_display = ("user", "otp", "is_verified", "verified_at", "created")
    search_fields = ("user__username", "user__email")
    raw_id_fields = ("user",)

    def get_queryset(self, request):
        return super().get_queryset(request)

    def has_add_permission(self, request):
        return False

    def get_ordering(self, request):
        return ["-created"]


class UserDropdownFilter(DropdownFilterForeignKey):
    def field_admin_ordering(self, field, request, model_admin):
        return ("first_name", "last_name", "email")


@admin.register(SaleLog)
class SaleLogAdmin(StaffAdmin):
    list_display = ("user", "event", "detail", "timestamp")
    list_filter = ("event", ("timestamp", DateRangeFilter), ("user", UserDropdownFilter))
    search_fields = ("user__email", "event", "detail")
    raw_id_fields = ("user",)
    readonly_fields = ("id", "user", "event", "detail", "timestamp")
    ordering = ("-timestamp",)

    def has_module_permission(self, request):
        return True

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(User, UserAdmin)
admin.site.unregister(SocialToken)
admin.site.unregister(SocialAccount)
admin.site.unregister(SocialApp)

# Unregister Django OAuth Toolkit admin models
admin.site.unregister(AccessToken)
admin.site.unregister(Application)
admin.site.unregister(Grant)
admin.site.unregister(IDToken)
admin.site.unregister(RefreshToken)

# Unregister Django Celery Beat admin models
admin.site.unregister(ClockedSchedule)
admin.site.unregister(CrontabSchedule)
admin.site.unregister(IntervalSchedule)
admin.site.unregister(PeriodicTask)
admin.site.unregister(SolarSchedule)
