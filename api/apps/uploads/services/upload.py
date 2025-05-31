from django.conf import settings
from django.core.files.storage import default_storage
from rest_framework.request import Request

from apps.core.utils import get_ip_address
from apps.uploads.exceptions import FileEmptyException
from apps.uploads.models import UploadFile
from apps.uploads.services.storage.base import BaseStorage


def upload_files(request: Request):
    files = request.FILES.getlist("file", [])
    if not files:
        raise FileEmptyException()
    user = get_user(request)
    upload_files_list = []
    base_storage = BaseStorage()
    for file in files:
        name = file.name
        file_name = base_storage.get_file_name(name)
        folder_name = request.data.get("folder_name", None)
        folder_name = base_storage.get_folder_name(folder_name)
        save_path = base_storage.get_file_path(str(folder_name), str(file_name))
        storage_path = default_storage.save(save_path, file)
        mime_type = base_storage.get_mime_type(file_name)
        size = file.size
        ip_address = get_ip_address(request)
        if settings.USE_S3:
            storage = "S3"
        else:
            storage = "Local"
        upload_file = base_storage.create_model_upload(
            file_path=storage_path,
            user=user,
            ip_address=ip_address,
            size=size,
            storage=storage,
            mime_type=mime_type,
        )
        upload_files_list.append(upload_file)
    created = UploadFile.objects.bulk_create(upload_files_list)
    return created


def get_user(request):
    user = request.user
    return None if user.is_anonymous else user
