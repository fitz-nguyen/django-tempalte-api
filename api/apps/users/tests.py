import datetime

from django.conf import settings
from django.urls import include, path, reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.core.utils import random_with_n_digits
from apps.users.exceptions import (
    EmailToResetNotExistException,
    PasswordResetOTPExpiredException,
    PasswordsNotMatchException,
    PasswordValidateError,
    UsernameAlreadyExistException,
    UsernameRegisteredWithThisEmailException,
)
from apps.users.models import ResetPasswordOTP, User

NOT_EXIST_EMAIL = "abc@gmail.com"
INVALID_PASSWORD = "123456"
INVALID_OTP = "111111"
NEW_PASSWORD_1 = "12345678@!"
NEW_PASSWORD_2 = "12345678@!@"


# Create your tests here.
class UserAuthTest(APITestCase):
    urlpatterns = [
        path("v1/", include("config.api")),
    ]

    def setUp(self):
        self.user = User.objects.create_user(
            username="test1",
            email="test1@gmail.com",
            password="12345678@",
            first_name="Unit",
            last_name="Test 1",
        )
        self.reset_password_otp = ResetPasswordOTP.objects.create(user=self.user, otp=random_with_n_digits(6, True))

        self.client = APIClient()
        url = reverse("token_obtain_pair")
        resp = self.client.post(
            url,
            {"email": "test1@gmail.com", "password": "12345678@"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue("access" in resp.data)
        self.token = resp.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION="Bearer " + str(self.token))

    def test_register_user(self):
        url = reverse("custom_register")
        data = {
            "username": "user1",
            "email": "user9@example.com",
            "password1": "123456@abc",
            "password2": "123456@abc",
        }
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_register_with_email_insensitive(self):
        url = reverse("custom_register")
        data = {
            "username": "user2",
            "email": "user2@example.com",
            "password1": "123456@abc",
            "password2": "123456@abc",
        }
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data["username"] = "user_2"
        data["email"] = "User2@example.com"
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["code"],
            UsernameRegisteredWithThisEmailException().code,
        )

    def test_register_with_username_insensitive(self):
        url = reverse("custom_register")
        data = {
            "username": "user3",
            "email": "user3@example.com",
            "password1": "123456@abc",
            "password2": "123456@abc",
        }
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data["username"] = "User3"
        data["email"] = "User4@example.com"
        response = self.client.post(url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], UsernameAlreadyExistException().code)

    def test_email_to_reset_not_exist_exception(self):
        self.url = reverse("rest_password_reset")
        data = {"email": NOT_EXIST_EMAIL}
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], EmailToResetNotExistException().code)

    def test_reset_password_with_valid_email(self):
        self.url = reverse("rest_password_reset")
        data = {"email": self.user.email}
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_email_to_reset_confirm_password_validate_error_exception(self):
        self.url = reverse("rest_password_reset_confirm")
        data = {
            "email": self.user.email,
            "new_password1": INVALID_PASSWORD,
            "new_password2": INVALID_PASSWORD,
            "otp": settings.TESTING_RESET_PASSWORD_OTP,
        }
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], PasswordValidateError().code)

    def test_email_to_reset_confirm_password_not_match_exception(self):
        self.url = reverse("rest_password_reset_confirm")
        data = {
            "email": self.user.email,
            "new_password1": NEW_PASSWORD_1,
            "new_password2": NEW_PASSWORD_2,
            "otp": settings.TESTING_RESET_PASSWORD_OTP,
        }
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], PasswordsNotMatchException().code)

    def test_password_reset_otp_invalid_exception(self):
        self.url = reverse("rest_password_reset_confirm")
        data = {
            "email": self.user.email,
            "new_password1": NEW_PASSWORD_1,
            "new_password2": NEW_PASSWORD_1,
            "otp": INVALID_OTP,
        }
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_otp_expired_exception(self):
        self.reset_password_otp.created = datetime.datetime.now() - datetime.timedelta(days=1)
        self.reset_password_otp.save()

        self.url = reverse("rest_password_reset_confirm")
        data = {
            "email": self.user.email,
            "new_password1": NEW_PASSWORD_1,
            "new_password2": NEW_PASSWORD_1,
            "otp": settings.TESTING_RESET_PASSWORD_OTP,
        }
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], PasswordResetOTPExpiredException().code)

    def test_reset_password_confirm_with_valid_email(self):
        self.reset_password_otp.created = datetime.datetime.now()
        self.reset_password_otp.save()

        self.url = reverse("rest_password_reset_confirm")
        data = {
            "email": self.user.email,
            "new_password1": NEW_PASSWORD_1,
            "new_password2": NEW_PASSWORD_1,
            "otp": settings.TESTING_RESET_PASSWORD_OTP,
        }
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
