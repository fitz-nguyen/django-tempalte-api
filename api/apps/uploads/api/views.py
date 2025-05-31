from rest_framework import generics, status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.helpers.s3 import S3Service
from apps.uploads.api.serializers import UploadFileSerializer
from apps.uploads.models import UploadFile
from apps.uploads.services.upload import upload_files
from apps.uploads.services.usercases import UploadFileService


class UploadFileView(generics.ListCreateAPIView):
    serializer_class = UploadFileSerializer
    parser_classes = (MultiPartParser,)
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        upload_file = upload_files(request=self.request)
        data = UploadFileSerializer(upload_file, many=True).data
        return Response(status=status.HTTP_201_CREATED, data=data)

    def get_queryset(self):
        return UploadFile.objects.all()


class S3PreSignedPost(APIView):
    permission_classes = (AllowAny,)

    @classmethod
    def get(cls, request, *args, **kwargs):
        return Response(
            UploadFileService.get_pre_signed_url(request),
            status=status.HTTP_200_OK,
        )


class DeleteS3FilesView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        file_paths = request.data.get("file_paths", [])
        if not file_paths:
            return Response({"error": "No file paths provided"}, status=status.HTTP_400_BAD_REQUEST)

        s3_service = S3Service()
        deleted_files = []
        failed_files = []

        for file_path in file_paths:
            try:
                s3_service.delete_file(file_path)
                deleted_files.append(file_path)
            except Exception as e:
                failed_files.append({"file_path": file_path, "error": str(e)})

        response_data = {"deleted_files": deleted_files, "failed_files": failed_files}

        return Response(response_data, status=status.HTTP_200_OK)
