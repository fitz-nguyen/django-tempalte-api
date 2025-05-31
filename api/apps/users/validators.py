import re

import django.contrib.auth.password_validation as password_validators
from django.core.exceptions import ValidationError
from django.core.validators import validate_email as validate_email_core
from rest_framework.serializers import ValidationError as DRFValidationError

from apps.core.utils import is_reset_password_otp_expired
from apps.users.exceptions import PasswordValidateError
from apps.users.models import ResetPasswordOTP, User


class EmailValidator(object):
    def __call__(self, email):
        if email.strip() == "":
            raise DRFValidationError("Email is required.", code=2000)

        try:
            validate_email_core(email)
        except ValidationError as error:
            raise DRFValidationError(error.messages[0], code=2007)


class PasswordValidator(object):
    def __init__(self, old_password=None):
        self.old_password = old_password

    def __call__(self, password):
        try:
            pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*\"'()+,-./:;<=>?[\]^_`{|}~])(?=.{8,})"
            if not re.match(pattern, password):
                raise PasswordValidateError("")
            password_validators.validate_password(password)
        except ValidationError as error:
            raise DRFValidationError(error.messages[0], code=2006)

        if self.old_password and self.old_password == password:
            raise DRFValidationError("Old password and new password can not be the same", code=2010)


class ResetPasswordOTPValidator(object):
    def __call__(self, otp):
        reset_password_otp = ResetPasswordOTP.objects.filter(otp=otp, is_verified=False).first()
        if not reset_password_otp:
            raise DRFValidationError("This OTP code is invalid or verified.", code=2012)

        if is_reset_password_otp_expired(reset_password_otp.created):
            raise DRFValidationError("This OTP code is expired. Please request new code.", code=2013)


class UsernameValidator(object):
    def __call__(self, username):
        user = User.objects.filter(username__iexact=username.lower()).first()
        if user:
            raise DRFValidationError("This username is invalid", code=2000)
        return username


class HoursAvailableValidator(object):
    def __call__(self, hours_available_per_week):
        if hours_available_per_week < 0 or hours_available_per_week > 168:
            raise DRFValidationError("Hours available must be between 0 and 168", code=2017)
