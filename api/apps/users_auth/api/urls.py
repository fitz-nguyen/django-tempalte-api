from dj_rest_auth.views import PasswordChangeView, PasswordResetConfirmView, PasswordResetView
from django.urls import path

from apps.users_auth.api.views import (
    CustomLoginView,
    CustomRegisterView,
    CustomTokenRefreshView,
    CustomVerifyEmailView,
    ForgotBlockWalkerUsernameView,
    ForgotUsernameView,
    ResendConfirmEmailView,
)

urlpatterns = [
    path("auth/registration/", CustomRegisterView.as_view(), name="custom_register"),
    path("auth/registration/verify-email/", CustomVerifyEmailView.as_view(), name="verify-email"),
    path("auth/registration/forgot-username/", ForgotUsernameView.as_view(), name="forgot-username"),
    path(
        "auth/registration/blockwalker/forgot-username/",
        ForgotBlockWalkerUsernameView.as_view(),
        name="block-walker-forgot-username",
    ),
    path("auth/password/change/", PasswordChangeView.as_view(), name="rest_password_change"),
    path("auth/password/reset/", PasswordResetView.as_view(), name="rest_password_reset"),
    path("auth/password/reset/confirm/", PasswordResetConfirmView.as_view(), name="rest_password_reset_confirm"),
    path("token/", CustomLoginView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("auth/registration/resend-email/", ResendConfirmEmailView.as_view(), name="resend_confirm_email"),
]
