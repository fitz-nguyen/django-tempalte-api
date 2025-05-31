from tempfile import NamedTemporaryFile

from apps.uploads.models import UploadFile
from apps.uploads.services.usercases import UploadFileService
from apps.users.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import include, path, reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase


class UploadsTest(APITestCase):
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
        self.file_path = "media/test/image.png"

    def test_upload_files(self):
        url = reverse("upload-file")

        image = NamedTemporaryFile(suffix=".png")
        data = {
            "file": SimpleUploadedFile(image.name, b"jpg"),
            "folder_name": "useom",
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data[0]["status"], "NEW")

    def test_mark_upload_file_used(self):
        UploadFile.objects.create(file_path=self.file_path, user=self.user)

        UploadFileService(user=self.user).mark_file_used(file_path=self.file_path)
        example_file = UploadFile.objects.filter(file_path=self.file_path, user=self.user).first()
        self.assertEqual(example_file.status, "USED")
