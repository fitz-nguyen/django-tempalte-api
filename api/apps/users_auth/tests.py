from django.urls import include, path, reverse
from rest_framework import status
from rest_framework.test import APITestCase

from apps.users.models import User


class UsersAuthTest(APITestCase):
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

    def test_login(self):
        url = reverse("token_obtain_pair")
        resp = self.client.post(
            url,
            {"email": "test1@gmail.com", "password": "12345678@"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue("access" in resp.data)
        self.assertTrue("refresh" in resp.data)

    def test_refresh_token(self):
        login_url = reverse("token_obtain_pair")
        refresh_url = reverse("token_refresh")
        resp = self.client.post(
            login_url,
            {"email": "test1@gmail.com", "password": "12345678@"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertTrue("access" in resp.data)
        self.assertTrue("refresh" in resp.data)
        refresh_token = resp.data["refresh"]
        resp = self.client.post(refresh_url, {"refresh": refresh_token}, format="json")
        self.assertTrue("access" in resp.data)
        self.assertTrue("refresh" in resp.data)
