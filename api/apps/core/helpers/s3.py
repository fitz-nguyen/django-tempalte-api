import boto3
import botocore
import botocore.config
from django.conf import settings
from google.cloud.storage import Bucket

from apps.core.exceptions import InvalidDataException


class S3Service:
    @classmethod
    def s3_client(cls):
        config = botocore.config.Config(read_timeout=900, connect_timeout=900, retries={"max_attempts": 2})
        return boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
            config=config,
        )

    def exists_key(self, key):
        try:
            # HeadObject operation will throw an exception if the key doesn't exist
            self.s3_client().head_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=key)
            return True
        except Exception as e:
            if e.response["Error"]["Code"] == "404":
                # Key not found
                return False
            else:
                # Handle other exceptions if needed
                raise InvalidDataException(e)

    def delete_file(self, filename):
        return self.s3_client().delete_object(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=filename,
        )

    def upload_file(self, file_path, s3_path):
        """
        Upload a file to S3 and return the full S3 URL.

        Args:
            file_path (str): Local file path to upload
            s3_path (str): Destination path in S3 (without media/ prefix)

        Returns:
            str: Full S3 URL of the uploaded file
        """
        try:
            with open(file_path, "rb") as file_obj:
                self.s3_client().upload_fileobj(file_obj, settings.AWS_STORAGE_BUCKET_NAME, s3_path)
            return f"{settings.AWS_MEDIA_URL}/{s3_path}"
        except Exception as e:
            raise InvalidDataException(f"Failed to upload file to S3: {str(e)}")
