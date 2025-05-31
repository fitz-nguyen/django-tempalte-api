import json

import boto3
import botocore.config
from django.conf import settings

from apps.core.utils import get_aws_lambda_export_csv_hook, get_datetime_now_to_string


class AWSLambdaService:
    @classmethod
    def get_lambda_client(cls):
        config = botocore.config.Config(read_timeout=900, connect_timeout=900, retries={"max_attempts": 0})
        return boto3.client(
            "lambda",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
            config=config,
        )

    @classmethod
    def export_csv_invoke(cls, payload: dict):
        client = cls.get_lambda_client()
        client.invoke(
            FunctionName=settings.LAMBDA_EXPORT_MAP_CSV_FUNCTION,
            LogType="Tail",
            InvocationType="Event",
            Payload=json.dumps(payload),
        )

    @classmethod
    def import_contact_status_invoke(cls, filepath: str, import_contact_support_status_id: str, csv_fields, user_id):
        client = cls.get_lambda_client()
        client.invoke(
            FunctionName=settings.LAMBDA_IMPORT_CONTACT_STATUS_FUNCTION,
            LogType="Tail",
            InvocationType="Event",
            Payload=json.dumps(
                {
                    "filepath": filepath,
                    "import_contact_support_status_id": str(import_contact_support_status_id),
                    "csv_fields": csv_fields,
                    "user_id": user_id,
                }
            ),
        )
