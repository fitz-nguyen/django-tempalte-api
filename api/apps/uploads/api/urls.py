from django.urls import path

from apps.uploads.api.views import DeleteS3FilesView, S3PreSignedPost, UploadFileView

urlpatterns = [
    path("", UploadFileView.as_view(), name="upload-file"),
    path("s3/pre-signed-post-url/", S3PreSignedPost.as_view()),
    path("s3/delete-files/", DeleteS3FilesView.as_view(), name="delete-s3-files"),
]
