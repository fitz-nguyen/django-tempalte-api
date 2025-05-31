from __future__ import absolute_import, unicode_literals

from urllib.parse import quote

from apps.systems.utils import SystemConfigCache
from django import forms
from django.conf import settings
from django.contrib.auth import password_validation
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm, UserChangeForm, UserCreationForm
from django.contrib.auth.tokens import PasswordResetTokenGenerator, default_token_generator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.core.helpers.branchio import generate_branch_io_link
from apps.users.choices import ADMIN, ADMIN_SITE, REGULAR, SALE
from apps.users.exceptions import PasswordsNotMatchException, PasswordValidateError
from apps.users.models import Company, User


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = "__all__"


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("company", "role", "first_name", "last_name", "email")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = user.email
        user.set_password(self.cleaned_data["password1"])
        user.created_via = ADMIN_SITE
        if commit:
            user.save()
        return user


class AdminUserCreationForm(CustomUserCreationForm):
    role = forms.CharField(
        initial=ADMIN,
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
    )

    def clean_role(self):
        return ADMIN


class RegularUserCreationForm(CustomUserCreationForm):
    role = forms.CharField(
        initial=REGULAR,
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
    )

    def clean_role(self):
        return REGULAR


class SalesRepresentativeCreationForm(CustomUserCreationForm):
    role = forms.CharField(
        initial=SALE,
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
    )

    def clean_role(self):
        return SALE


class CustomPasswordResetForm(PasswordResetForm):
    def save(
        self,
        domain_override=None,
        subject_template_name="registration/password_reset_subject.txt",
        email_template_name="registration/password_reset_email.txt",
        use_https=False,
        token_generator=default_token_generator,
        from_email=None,
        request=None,
        html_email_template_name="registration/password_reset_email.html",
        extra_email_context=None,
    ):
        """
        Generate a one-use only link for resetting password and send it to the
        user.
        """
        email = self.cleaned_data["email"].lower()

        for user in self.get_users(email):
            domain = settings.FRONTEND_BASE_URL.rstrip("/")
            token = PasswordResetTokenGenerator().make_token(user)
            if settings.USE_BRANCH_IO and user.role == SALE:
                reset_link = generate_branch_io_link({"action": "reset-password", "token": token, "email": user.email})
            else:
                slug = f"/login/?token={token}&email={quote(user.email)}&type=reset-password/"
                reset_link = domain + slug

            context = {
                "email": email,
                "name": user.name,
                "user": user,
                "username": user.username,
                "reset_link": reset_link,
                "footer_image_url": SystemConfigCache().email_footer_url,
                **(extra_email_context or {}),
            }
            self.send_mail(
                subject_template_name,
                email_template_name,
                context,
                from_email,
                email,
                html_email_template_name=html_email_template_name,
            )


class CustomSetPasswordForm(SetPasswordForm):
    def clean_new_password2(self):
        password1 = self.cleaned_data.get("new_password1")
        password2 = self.cleaned_data.get("new_password2")
        if password1 and password2 and password1 != password2:
            raise PasswordsNotMatchException()
        try:
            password_validation.validate_password(password2, self.user)
        except ValidationError as error:
            raise PasswordValidateError(error.messages[0])
        return password2

    def save(self, commit=True):
        password = self.cleaned_data["new_password1"]
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user


class CompanyAdminForm(forms.ModelForm):
    # Business Address fields
    city = forms.CharField(
        label=_("City"),
        max_length=100,
        required=True,
    )
    label = forms.CharField(
        label=_("Full Address Label"),
        max_length=255,
        required=True,
        help_text=_("Full address display (e.g. '12065, Clifton Park, NY, United States')"),
    )
    state = forms.CharField(
        label=_("State"),
        max_length=100,
        required=True,
    )
    county = forms.CharField(
        label=_("County"),
        max_length=100,
        required=False,
    )
    state_code = forms.CharField(
        label=_("State Code"),
        max_length=10,
        required=True,
    )
    postal_code = forms.CharField(
        label=_("Postal Code"),
        max_length=20,
        required=True,
    )
    country_code = forms.CharField(
        label=_("Country Code"),
        max_length=10,
        required=True,
    )
    country_name = forms.CharField(
        label=_("Country Name"),
        max_length=100,
        required=True,
    )

    # Region served fields
    region_data = forms.CharField(
        label=_("Region Data"),
        widget=forms.Textarea(attrs={"rows": 5}),
        help_text=_("Enter one region per line in format: zip,city,state"),
        required=True,
    )

    class Meta:
        model = Company
        fields = "__all__"
        exclude = ("region_served", "business_address")  # Exclude fields that will be handled in the form

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:  # If editing existing company
            # Set business_address fields
            business_address = self.instance.business_address or {}
            self.fields["city"].initial = business_address.get("city", "")
            self.fields["label"].initial = business_address.get("label", "")
            self.fields["state"].initial = business_address.get("state", "")
            self.fields["county"].initial = business_address.get("county", "")
            self.fields["state_code"].initial = business_address.get("state_code", "")
            self.fields["postal_code"].initial = business_address.get("postal_code", "")
            self.fields["country_code"].initial = business_address.get("country_code", "")
            self.fields["country_name"].initial = business_address.get("country_name", "")

            # Set region_served fields
            region_served = self.instance.region_served or []
            region_data = "\n".join([f"{r['zip']},{r['city']},{r['state']}" for r in region_served])
            self.fields["region_data"].initial = region_data

    def clean(self):
        cleaned_data = super().clean()

        # Process business_address fields
        business_address = {
            "city": cleaned_data.get("city", ""),
            "label": cleaned_data.get("label", ""),
            "state": cleaned_data.get("state", ""),
            "county": cleaned_data.get("county", ""),
            "state_code": cleaned_data.get("state_code", ""),
            "postal_code": cleaned_data.get("postal_code", ""),
            "country_code": cleaned_data.get("country_code", ""),
            "country_name": cleaned_data.get("country_name", ""),
        }

        # Add business_address to cleaned_data
        cleaned_data["business_address"] = business_address

        # Process region data
        region_data = cleaned_data.get("region_data", "")
        region_served = []

        for line in region_data.split("\n"):
            if not line.strip():
                continue
            try:
                zip_code, city, state = [item.strip() for item in line.split(",")]
                if not zip_code.isalnum():
                    self.add_error("region_data", _(f"Invalid zipcode format: {zip_code}"))
                region_served.append({"zip": zip_code, "city": city, "state": state})
            except ValueError:
                self.add_error("region_data", _(f"Invalid format. Expected: zip,city,state. Got: {line}"))

        if not region_served:
            self.add_error("region_data", _("At least one region must be specified"))

        # Add region_served to cleaned_data
        cleaned_data["region_served"] = region_served

        if self.instance.pk:  # If editing existing company
            if Company.objects.filter(business_name__iexact=cleaned_data.get("business_name", "")).exists():
                self.add_error("business_name", _("There is exists a company with that name."))
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Set the business_address field from our processed data
        instance.business_address = self.cleaned_data.get("business_address", {})

        # Set the region_served field from our processed data
        instance.region_served = self.cleaned_data.get("region_served", [])

        # Combine phone country code and phone number to create e164 format
        if instance.contact_phone_number and instance.contact_phone_country_code:
            instance.contact_phone_e164 = instance.contact_phone_country_code + instance.contact_phone_number

        if commit:
            instance.save()

        return instance
