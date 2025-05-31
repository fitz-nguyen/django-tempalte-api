from django.urls import include, path, reverse
from faker import Faker
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from apps.notification import choices
from apps.notification.exceptions import ArchiveNotificationIDsEmptyException, ReadNotificationIDsEmptyException
from apps.notification.models import Category, Message
from apps.users.models import User


class NotificationTest(APITestCase):
    urlpatterns = [
        path("v1/", include("config.api")),
    ]

    def setUp(self):
        self.user = User.objects.create_user(
            username="test1",
            email="test1@gmail.com",
            password="12345678@",
            first_name="Unit",
            last_name="Test",
        )
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

        fake = Faker()
        self.category = Category.objects.create(name=fake.sentence(), description=fake.text())
        self.messages = []
        for index in range(20):
            self.messages.append(
                Message.objects.create(
                    category=self.category,
                    verb=fake.word(),
                    user=self.user,
                    topic=fake.sentence(),
                    title=fake.sentence(),
                    content=fake.text(),
                    status=choices.MESSAGE_STATUS_SENT,
                )
            )

    def test_get_notifications(self):
        self.url = reverse("messages")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 20)

    def test_get_notifications_badge(self):
        self.url = reverse("messages-badge")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["badge"], 20)

    def test_mark_read_notifications(self):
        # Mark as read notification id list
        self.url = reverse("messages-read")
        data = {"ids": [self.messages[0].pk, self.messages[1].pk], "all": "N"}
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Get notification badge
        self.url = reverse("messages-badge")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["badge"], 18)

    def test_mark_read_notifications_empty_id_list_exception(self):
        # Mark as read notification id list
        self.url = reverse("messages-read")
        data = {"ids": [], "all": "N"}
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], ReadNotificationIDsEmptyException().code)

    def test_mark_read_notifications_mark_all_read(self):
        # Mark as read all notifications
        self.url = reverse("messages-read")
        data = {"ids": [], "all": "Y"}
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Get notification badge
        self.url = reverse("messages-badge")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["badge"], 0)

    def test_archive_notifications(self):
        # Archive notification id list
        self.url = reverse("messages-archive")
        data = {"ids": [self.messages[0].pk, self.messages[1].pk], "all": "N"}
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Get notifications after archive
        self.url = reverse("messages")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 18)

    def test_archive_notifications_empty_id_list_exception(self):
        # Mark as read notification id list
        self.url = reverse("messages-archive")
        data = {"ids": [], "all": "N"}
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], ArchiveNotificationIDsEmptyException().code)

    def test_archive_notifications_archive_all(self):
        # Archive all notifications
        self.url = reverse("messages-archive")
        data = {"ids": [], "all": "Y"}
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        # Get notifications after archive
        self.url = reverse("messages")
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)
