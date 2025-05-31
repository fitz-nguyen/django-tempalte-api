from allauth.account.models import EmailConfirmation, EmailConfirmationHMAC
from allauth.account.utils import complete_signup
from apps.users.api.serializers import (
    ResendConfirmBodySerializer,
    ResponseTokenSerializer,
    UserLoginBodySerializer,
    UserSerializer,
    UserTokenRefreshSerializer,
)
from apps.users.choices import SALE
from apps.users.models import User
from apps.users.services import add_sale_logs
from apps.users_auth.exceptions import (
    EmailConfirmationIsNotValidException,
    UserIsNotActiveException,
)
from apps.users_auth.services import (
    forgot_username,
    resend_confirmation_email,
    send_under_review_mail,
)
from apps.users_auth.tasks import send_confirm_email_task
from dj_rest_auth.app_settings import api_settings
from dj_rest_auth.models import get_token_model
from dj_rest_auth.registration.views import RegisterView, VerifyEmailView
from dj_rest_auth.utils import jwt_encode
from dj_rest_auth.views import LoginView
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenRefreshView


class CustomRegisterView(RegisterView):
    def post(self, request, *args, **kwargs):
        # Call the create method to handle the normal post logic
        response = self.create(request, *args, **kwargs)
        email = self.request.data.get("email")
        transaction.on_commit(lambda: send_confirm_email_task.delay(email))
        return response

    def perform_create(self, serializer):
        user = serializer.save(self.request)
        if settings.ACCOUNT_EMAIL_VERIFICATION == settings.ACCOUNT_EMAIL_VERIFICATION_MANDATORY:
            if api_settings.USE_JWT:
                self.access_token, self.refresh_token = jwt_encode(user)
            elif not api_settings.SESSION_LOGIN:
                # Session authentication isn't active either, so this has to be
                #  token authentication
                api_settings.TOKEN_CREATOR(self.token_model, user, serializer)
            complete_signup(
                self.request._request,
                user,
                settings.ACCOUNT_EMAIL_VERIFICATION_MANDATORY,
                None,
            )
        return user

    def get_response_data(self, user):
        if settings.ACCOUNT_EMAIL_VERIFICATION == settings.ACCOUNT_EMAIL_VERIFICATION_MANDATORY:
            return {"detail": _("Verification e-mail sent.")}
        elif (
            settings.ACCOUNT_EMAIL_VERIFICATION != settings.ACCOUNT_EMAIL_VERIFICATION_MANDATORY
            and settings.SEND_UNDER_REVIEW_EMAIL_AFTER_COMPLETED_SIGN_UP
        ):
            send_under_review_mail(user.email)
            return {"detail": "Under Review email sent."}
        return UserSerializer(user).data


class CustomLoginView(LoginView):
    def get_response(self):
        serializer_class = TokenObtainPairSerializer()
        serializer = serializer_class.get_token(self.user)

        access = serializer.access_token
        User.objects.filter(id=self.user.pk).update(last_login=timezone.now())

        # Track SALE user login using the service
        add_sale_logs(user=self.user, event="Logged In", detail="Logged into the Django Template App")

        data = {
            "refresh": str(serializer),
            "access": str(access),
        }
        return Response(ResponseTokenSerializer(data).data, status=status.HTTP_200_OK)

    def login(self):
        self.user = self.serializer.validated_data["user"]
        token_model = get_token_model()

        if getattr(settings, "REST_USE_JWT", False):
            self.token = jwt_encode(self.user)
        else:
            self.token = api_settings.TOKEN_CREATOR(token_model, self.user, self.serializer)

    @swagger_auto_schema(
        request_body=UserLoginBodySerializer,
        responses={200: openapi.Response("response description", ResponseTokenSerializer)},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = UserTokenRefreshSerializer

    @swagger_auto_schema(
        responses={200: openapi.Response("response description", ResponseTokenSerializer)},
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ResendConfirmEmailView(APIView):
    permission_classes = (AllowAny,)

    @swagger_auto_schema(request_body=ResendConfirmBodySerializer)
    def post(self, request):
        email = request.data["email"]
        resend_confirmation_email(email=email)
        return Response({"detail": _("Verification e-mail sent.")}, status=status.HTTP_200_OK)


class CustomVerifyEmailView(VerifyEmailView):
    def get_object(self, queryset=None):
        key = self.kwargs["key"]
        emailconfirmation = EmailConfirmationHMAC.from_key(key)
        if not emailconfirmation:
            if queryset is None:
                queryset = self.get_queryset()
            try:
                emailconfirmation = queryset.get(key=key.lower())
            except EmailConfirmation.DoesNotExist:
                raise EmailConfirmationIsNotValidException()
        return emailconfirmation

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.kwargs["key"] = serializer.validated_data["key"]
        confirmation = self.get_object()
        confirmation.confirm(self.request)
        user = confirmation.email_address.user
        user.email_verified = True
        user.save()
        if not user.is_active:
            if not user.is_sent_mail_approve_account:
                # trigger send under review
                send_under_review_mail(user.email)
                return Response({"detail": "Under Review email sent."}, status=status.HTTP_200_OK)
            raise UserIsNotActiveException()

        serializer_class = TokenObtainPairSerializer()
        serializer = serializer_class.get_token(user)
        access = serializer.access_token
        data = {
            "refresh": str(serializer),
            "access": str(access),
        }
        return Response(data, status=status.HTTP_200_OK)


class ForgotUsernameView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        forgot_username(email)
        data = {"success": True}
        return Response(data, status=status.HTTP_200_OK)


class ForgotBlockWalkerUsernameView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        forgot_username(email, role=SALE)
        data = {"success": True}
        return Response(data, status=status.HTTP_200_OK)
