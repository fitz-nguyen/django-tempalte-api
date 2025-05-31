from allauth.account.adapter import get_adapter
from allauth.account.utils import user_email, user_field, user_username
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer, PasswordChangeSerializer, PasswordResetSerializer
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken

from apps.core.utils import check_fake_email, get_media_url
from apps.users.choices import APPROVED, REGULAR, SALE
from apps.users.exceptions import (
    EmailRegisteredNotVerifiedException,
    EmailToResetNotExistException,
    EmailValidateError,
    LogInException,
    NewPasswordSameAsOldException,
    PasswordResetTokenException,
    PasswordResetTokenInvalidException,
    PhoneAlreadyExistException,
    UserAccountDisabledException,
    UsernameRegisteredWithThisEmailException,
    UserRoleIsNotValidException,
)
from apps.users.forms import CustomPasswordResetForm, CustomSetPasswordForm
from apps.users.models import Company, User
from apps.users.services import get_user, handle_avatar_when_sign_up, update_user
from apps.users.signals import user_signup_signal
from apps.users.validators import EmailValidator, PasswordValidator
from apps.users_auth.exceptions import CompanyIsNotActiveException, UserIsNotActiveException, UserIsNotApprovedException


def validate_region_served(region_served):
    """
    Validate region_served data structure
    """
    if not isinstance(region_served, list):
        raise serializers.ValidationError(_("Region served must be a list"))

    if not region_served:
        raise serializers.ValidationError(_("At least one region must be specified"))

    for region in region_served:
        if not isinstance(region, dict):
            raise serializers.ValidationError(_("Each region must be a dictionary"))

        required_fields = ["zip", "city", "state"]
        for field in required_fields:
            if field not in region:
                raise serializers.ValidationError(_(f"Each region must contain {field}"))
            if not isinstance(region[field], str):
                raise serializers.ValidationError(_(f"{field} must be a string"))

        # Validate zipcode format
        if not region["zip"].isalnum():
            raise serializers.ValidationError(_(f"Invalid zipcode format: {region['zip']}"))

    return region_served


class CompanySerializer(serializers.ModelSerializer):
    dashboard_data_uri = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = (
            "id",
            "business_name",
            "business_address",
            "region_served",
            "is_active",
            "metadata",
            "dashboard_data_uri",
            "contact_firstname",
            "contact_lastname",
            "contact_phone_number",
            "contact_phone_country_code",
            "contact_phone_e164",
            "centre_point",
            "is_csv_processing",
        )
        read_only_fields = ("id", "dashboard_data_uri", "contact_phone_e164", "is_csv_processing")

    def validate_region_served(self, value):
        return validate_region_served(value)

    @classmethod
    def get_dashboard_data_uri(cls, obj):
        return get_media_url(obj.dashboard_data_uri.replace("media/", "")) if obj.dashboard_data_uri else ""

    def save(self, **kwargs):
        business_name = self.validated_data.get("business_name")

        # Try to get existing company by business_name
        try:
            company = Company.objects.get(business_name__iexact=business_name)
            # Update existing company
            for attr, value in self.validated_data.items():
                setattr(company, attr, value)
            company.save()
            return company
        except Company.DoesNotExist:
            # Create new company if doesn't exist
            return super().save(**kwargs)


class CompanyListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = (
            "id",
            "business_name",
            "business_address",
            "region_served",
            "contact_firstname",
            "contact_lastname",
            "contact_phone_number",
            "contact_phone_country_code",
            "centre_point",
            "is_active",
        )


class UserSimpleInfoSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "avatar",
            "display_name",
        )

    @classmethod
    def get_avatar(cls, obj):
        return obj.get_avatar()

    @classmethod
    def get_display_name(cls, obj):
        return obj.get_display_name()


class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()
    company = CompanySerializer()

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "avatar",
            "display_name",
            "profile_complete",
            "email_verified",
            "notification",
            "company",
            "status",
            "role",
        )
        read_only_fields = ("username", "display_name", "company")

    email = serializers.EmailField(required=True, allow_blank=False, allow_null=False, validators=[EmailValidator()])

    @classmethod
    def get_avatar(cls, obj):
        return obj.get_avatar()

    @classmethod
    def get_display_name(cls, obj):
        return obj.get_display_name()

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["email"] = instance.email if not check_fake_email(instance.email) else None
        return ret

    def update(self, instance: User, validated_data):
        avatar = self.initial_data.get("avatar", instance.avatar)

        if "phone" in self.validated_data:
            if User.objects.filter(phone__iexact=self.validated_data.get("phone")).exclude(id=instance.id).exists():
                raise PhoneAlreadyExistException()

        if "email" in self.validated_data:
            if (
                User.objects.filter(email__iexact=self.validated_data.get("email").lower())
                .exclude(id=instance.id)
                .exists()
            ):
                raise UsernameRegisteredWithThisEmailException()
        instance = update_user(instance, validated_data, avatar)
        return instance


class CheckInviteEmailSerializer(serializers.Serializer):
    emails = serializers.CharField(required=False)
    candidate_id = serializers.CharField(required=False)


class CheckInviteExpiredSerializer(serializers.Serializer):
    email = serializers.CharField(required=False)
    candidate_code = serializers.CharField(required=False)
    invite_id = serializers.CharField(required=False)


class UserProfileSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):  # noqa
        model = User
        fields = UserSerializer.Meta.fields  # noqa

    @classmethod
    def get_profile_complete(cls, obj):
        return True if not check_fake_email(obj.email) else False


class UserRegisterSerializer(RegisterSerializer):
    avatar = serializers.CharField(max_length=1000, required=False, default="")
    email = serializers.EmailField(required=True, allow_null=False, validators=[EmailValidator()])
    first_name = serializers.CharField(max_length=30)
    last_name = serializers.CharField(max_length=150)
    password1 = serializers.CharField(write_only=True, validators=[PasswordValidator()])
    password2 = serializers.CharField(write_only=True, validators=[PasswordValidator()])
    # Company fields
    business_name = serializers.CharField(max_length=255)
    business_address = serializers.JSONField()
    region_served = serializers.JSONField()

    contact_firstname = serializers.CharField(max_length=100)
    contact_lastname = serializers.CharField(max_length=100)
    contact_phone_number = serializers.CharField(max_length=20)
    contact_phone_country_code = serializers.CharField(max_length=10)

    def validate_business_address(self, value):
        return value
        # if not value.strip():
        #     raise serializers.ValidationError(_("Business address cannot be empty"))
        # return value.strip()

    def validate_region_served(self, value):
        return validate_region_served(value)

    def validate(self, data):
        if "email" in data:
            if User.objects.filter(email__iexact=data.get("email").lower()).exists():
                raise UsernameRegisteredWithThisEmailException()
        data["email"] = data["email"].lower()
        # if data["password1"] != data["password2"]:
        #     raise serializers.ValidationError(_("The two password fields didn't match."))
        return data

    def save_user(self, request, user, form, commit=True):
        data = form.cleaned_data
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        email = data.get("email")
        username = data.get("username")
        user_email(user, email)
        user_username(user, username)
        if first_name:
            user_field(user, "first_name", first_name)
        if last_name:
            user_field(user, "last_name", last_name)
        if "password1" in data:
            user.set_password(data["password1"])
        else:
            user.set_unusable_password()
        adapter = get_adapter()
        user.username = adapter.generate_unique_username([first_name, last_name, email, username, "user"])
        user.avatar = self.validated_data.get("avatar")
        user.first_name = self.validated_data.get("first_name", "")
        user.last_name = self.validated_data.get("last_name", "")

        # Handle Company creation/linking
        business_name = self.validated_data.get("business_name")
        company = None

        try:
            # Try to get existing company
            company = Company.objects.get(business_name__iexact=business_name)
        except Company.DoesNotExist:
            # Create new company if doesn't exist
            company = Company.objects.create(
                business_name=business_name,
                business_address=self.validated_data.get("business_address"),
                region_served=self.validated_data.get("region_served"),
                contact_firstname=self.validated_data.get("contact_firstname", ""),
                contact_lastname=self.validated_data.get("contact_lastname", ""),
                contact_phone_number=self.validated_data.get("contact_phone_number", ""),
                contact_phone_country_code=self.validated_data.get("contact_phone_country_code", ""),
                is_active=False,
            )

            # Set contact_phone_e164 if both phone number and country code are provided
            if company.contact_phone_number and company.contact_phone_country_code:
                company.contact_phone_e164 = company.contact_phone_country_code + company.contact_phone_number
                company.save()

        # Link user to company
        user.company = company

        user.display_name = f"{user.first_name} {user.last_name}"

        user.save()
        handle_avatar_when_sign_up(user.avatar)
        user_signup_signal.send(sender=User, user=user)

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        self.save_user(request, user, self)
        return user


class UserPasswordResetSerializer(PasswordResetSerializer):
    password_reset_form_class = CustomPasswordResetForm


class UserPasswordChangeSerializer(PasswordChangeSerializer):
    old_password = serializers.CharField(max_length=128, allow_blank=True)
    new_password1 = serializers.CharField(
        max_length=128, allow_blank=True, validators=[PasswordValidator(old_password)]
    )
    new_password2 = serializers.CharField(max_length=128, allow_blank=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs["new_password1"] == attrs["old_password"]:
            raise NewPasswordSameAsOldException()
        return attrs


class UserPasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for requesting a password reset e-mail.
    """

    new_password1 = serializers.CharField(max_length=128)
    new_password2 = serializers.CharField(max_length=128)
    email = serializers.CharField(max_length=100)
    token = serializers.CharField(max_length=128)
    set_password_form_class = CustomSetPasswordForm

    def custom_validation(self, attrs):
        pass

    def validate(self, attrs):
        email = attrs.get("email")
        token = attrs.get("token")
        user = User.objects.get(email__iexact=email)
        if default_token_generator.check_token(user=user, token=token):
            self.set_password_form = self.set_password_form_class(user=user, data=attrs)
            if (
                not self.set_password_form.is_valid()
                and self.set_password_form.errors
                and self.set_password_form.errors.values()
            ):
                raise PasswordResetTokenException(list(self.set_password_form.errors.values())[0])
        else:
            raise PasswordResetTokenInvalidException
        attrs[email] = email
        return attrs

    def save(self):
        return self.set_password_form.save()


class UserTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        refresh = RefreshToken(attrs["refresh"])

        # check exist user
        user_id = refresh.payload.get("id")
        get_user(user_id=user_id)

        data = {"access": str(refresh.access_token)}

        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    # Attempt to blacklist the given refresh token
                    refresh.blacklist()
                except AttributeError:
                    # If blacklist app not installed, `blacklist` method will
                    # not be present
                    pass

            refresh.set_jti()
            refresh.set_exp()

            data["refresh"] = str(refresh)

        return data


class ResponseTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField(read_only=True)
    access = serializers.CharField(read_only=True)
    enabled_2fa = serializers.BooleanField(read_only=True)


class UserLoginBodySerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class ResendConfirmBodySerializer(serializers.Serializer):
    email = serializers.CharField(required=True)


class UserLoginSerializer(LoginSerializer):
    platform = serializers.CharField(required=False, default="mobile")

    def _validate_email(self, email, password):
        if email and password:
            try:
                validate_email(email)
            except ValidationError:
                raise EmailValidateError("Please enter a valid email address.")

            if not User.objects.filter(email__iexact=email).exists():
                raise EmailToResetNotExistException("This email is not registered. Please sign up.")

            try:
                user = self.authenticate(email=email, password=password)
            except Exception:
                raise LogInException("The password you entered is incorrect. Please try again.")
        else:
            raise LogInException("Must include either username or email and password.")

        return user

    def _validate_username(self, username, password):
        if username and password:
            try:
                user = User.objects.get(username__iexact=username)
                if user.check_password(password) and user.is_active:
                    return user
            except User.DoesNotExist:
                raise LogInException("Unable to log in with provided credentials.")
            raise LogInException("The password you entered is incorrect. Please try again.")
        else:
            raise LogInException("Must include either username or email and password.")

    def _validate_username_email(self, username, email, password):
        if email and password:
            try:
                validate_email(email)
            except ValidationError:
                raise EmailValidateError("Please enter a valid email address.")

            if not User.objects.filter(email__iexact=email).exists():
                raise EmailToResetNotExistException("This email is not registered. Please sign up.")

            try:
                user = self.authenticate(email=email, password=password)
            except Exception:
                raise LogInException("The password you entered is incorrect. Please try again.")
        elif username and password:
            user = self.authenticate(username=username, password=password)
        else:
            raise LogInException("Must include either username or email and password.")

        return user

    def authenticate(self, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(settings.ACCOUNT_AUTHENTICATION_METHOD)
        if username is None or password is None:
            return
        try:
            user = User._default_manager.get(**{settings.ACCOUNT_AUTHENTICATION_METHOD: username})
        except User.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user (#20760).
            User().set_password(password)
        else:
            if user.check_password(password):
                return user

    def validate(self, attrs):
        username = attrs.get("username")
        email = attrs.get("email")
        password = attrs.get("password")
        platform = attrs.get("platform", "mobile")  # Get platform value

        user = None

        if "allauth" in settings.INSTALLED_APPS:
            # Authentication through email
            if settings.ACCOUNT_AUTHENTICATION_METHOD == settings.ACCOUNT_AUTHENTICATION_METHOD_EMAIL:
                user = self._validate_email(email, password)

            # Authentication through username
            elif settings.ACCOUNT_AUTHENTICATION_METHOD == settings.ACCOUNT_AUTHENTICATION_METHOD_USERNAME:
                user = self._validate_username(username, password)

            # Authentication through either username or email
            else:
                user = self._validate_username_email(username, email, password)

        else:
            # Authentication without using allauth
            if email:
                username = User.objects.get(email=email)

            if username:
                user = self._validate_username_email(username, "", password)

        # Did we get back an active user?
        if user:
            # Skip email verification, status, and company validation for staff and admin users
            if not user.is_staff and not user.is_superuser:
                # Check if user is SALE role trying to login from web platform
                if platform == "web" and user.role == SALE:
                    raise UserRoleIsNotValidException("Sales representatives cannot log in via web platform.")

                # Check if user is REGULAR role trying to login from mobile platform
                if platform == "mobile" and user.role == REGULAR:
                    raise UserRoleIsNotValidException("Regular users cannot log in via mobile platform.")
                if not user.is_active:
                    raise UserIsNotActiveException()

                if not user.email_verified:
                    raise EmailRegisteredNotVerifiedException()
                if user.status != APPROVED:
                    raise UserIsNotApprovedException()

                company = user.company
                if not company or not company.is_active:
                    raise CompanyIsNotActiveException
            else:
                if platform == "web":
                    raise UserRoleIsNotValidException("Admin cannot log in via web platform.")

        else:
            raise LogInException()

        attrs["user"] = user
        attrs["username"] = username
        return attrs
