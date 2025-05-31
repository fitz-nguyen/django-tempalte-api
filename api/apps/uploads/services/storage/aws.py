from typing import List

import boto3
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.request import Request

from apps.core.utils import get_ip_address
from apps.uploads.exceptions import S3InvalidArgumentException
from apps.uploads.services.storage.base import BaseStorage

User = get_user_model()


class AWSStorage(BaseStorage):
    @classmethod
    def generate_pre_signed_url(cls, storage_path: str, fields: dict = None, conditions: List[dict] = None) -> dict:
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        s3 = boto3.client("s3")
        pre_signed_post = s3.generate_presigned_post(
            Bucket=bucket_name,
            Key=storage_path,
            Fields=fields,
            Conditions=conditions,
            ExpiresIn=settings.S3_PRE_SIGNED_POST_URL_EXPIRES,
        )
        return pre_signed_post

    @classmethod
    def get_pre_signed_url(cls, request: Request) -> dict:
        data = request.query_params
        folder = data.get("folder_name", "")
        file_name = data.get("file_name", "")
        content_type = data.get("file_type", "")
        is_public = data.get("is_public", False)
        file_size = data.get("file_size", 0)
        ip_address = get_ip_address(request)
        user = request.user
        # get file path
        file_path = cls.get_file_path(folder, file_name)

        # Generate pre-signed url
        fields = {"Content-Type": content_type}
        conditions = [{"Content-Type": content_type}]
        if is_public:
            acl = {"acl": "public-read"}
            fields.update(acl)
            conditions.append(acl)
        try:
            res = cls.generate_pre_signed_url(file_path, fields=fields, conditions=conditions)
            storage = res.get("url", "")
            fields = res.get("fields", {})
        except Exception:
            raise S3InvalidArgumentException()

        if fields:
            # save to database
            if user.is_anonymous:
                user = None
            cls().create_upload_file_model(
                file_path=file_path,
                ip_address=ip_address,
                storage=storage,
                mime_type=content_type,
                size=file_size,
                user=user,
            )
        return res

    @classmethod
    def generate_public_url(cls, file_path) -> str:
        if not file_path:
            return ""
        bucket_name = settings.AWS_BUCKET_NAME
        client = boto3.client("s3")
        return client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": file_path},
            ExpiresIn=100,
        )
