from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.settings import api_settings

from apps.users.choices import APPROVED
from apps.users.exceptions import LogInException
from apps.users.models import User
from apps.users_auth.exceptions import (
    CompanyIsNotActiveException,
    TokenExpiredException,
    UserIsNotActiveException,
    UserIsNotApprovedException,
)


class CustomJWTAuthentication(JWTAuthentication):
    def get_validated_token(self, raw_token):
        """
        Validates an encoded JSON web token and returns a validated token
        wrapper object.
        """
        messages = []
        for AuthToken in api_settings.AUTH_TOKEN_CLASSES:
            try:
                return AuthToken(raw_token)
            except TokenError as e:
                messages.append(
                    {
                        "token_class": AuthToken.__name__,
                        "token_type": AuthToken.token_type,
                        "message": e.args[0],
                    }
                )
        raise TokenExpiredException()

    def get_user(self, validated_token):
        """
        Attempts to find and return a user using the given validated token.
        """
        try:
            user_id = validated_token[api_settings.USER_ID_CLAIM]
        except KeyError:
            raise InvalidToken(_("Token contained no recognizable user identification"))

        try:
            user = User.objects.get(**{api_settings.USER_ID_FIELD: user_id})
        except User.DoesNotExist:
            raise LogInException()

        # Set impersonal flag from token
        user.is_impersonal_user = validated_token.get("is_impersonal_user", False)

        # Skip active and status validation for impersonal users
        if not user.is_impersonal_user:
            if not user.is_active:
                raise UserIsNotActiveException()
            if user.status != APPROVED:
                raise UserIsNotApprovedException()

        # Skip company validation for staff, superusers, and impersonal users
        if not user.is_staff and not user.is_superuser and not user.is_impersonal_user:
            company = user.company
            if not company or not company.is_active:
                raise CompanyIsNotActiveException

        return user
