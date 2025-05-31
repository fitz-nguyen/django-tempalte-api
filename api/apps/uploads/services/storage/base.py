import re
from mimetypes import MimeTypes
from re import sub
from typing import Optional

from apps.core.utils import get_storage_path, random_with_n_digits
from apps.uploads.exceptions import FileEmptyException, FolderNameEmptyException
from apps.uploads.models import UploadFile
from apps.uploads.signals import dispatch_uploaded_file
from apps.users.models import User


class BaseStorage(object):
    @classmethod
    def get_file_name(cls, name: str) -> str:
        random_name = str(random_with_n_digits(6))
        name = re.sub(r"\.(?![^.]*$)", "_", name)
        file_name, file_ext = name.split(".")
        prefix_name = sub("[^A-Za-z0-9]+", "", file_name)
        file_name = f"{prefix_name}{random_name}.{file_ext}"
        return file_name

    @classmethod
    def get_folder_name(cls, folder_name: str) -> str:
        if folder_name:
            return sub("[^A-Za-z0-9]+", "", folder_name)
        else:
            raise FolderNameEmptyException()

    @classmethod
    def get_file_path(cls, folder_name: str, file_name: str) -> str:
        if file_name:
            file_name = cls.get_file_name(file_name)
        else:
            raise FileEmptyException()
        folder = cls.get_folder_name(folder_name)
        return get_storage_path(file_name, folder)

    @classmethod
    def get_mime_type(cls, file_name: str) -> Optional[str]:
        mime = MimeTypes()
        return mime.guess_type(file_name)[0]

    def create_upload_file_model(
        self,
        file_path: str,
        ip_address: str,
        storage: str,
        mime_type: str,
        size: int = None,
        user: User = None,
    ):
        upload_file = self.create_model_upload(file_path, ip_address, storage, mime_type, size, user)

        return upload_file.save()

    @classmethod
    def create_model_upload(
        cls,
        file_path: str,
        ip_address: str,
        storage: str,
        mime_type: str,
        size: int = None,
        user: User = None,
    ):
        upload_file = UploadFile(
            file_path=file_path,
            user=user,
            ip_address=ip_address,
            size=size,
            storage=storage,
            mime_type=mime_type,
        )
        dispatch_uploaded_file.send(sender=upload_file.__class__, created=True, upload_file=upload_file)
        return upload_file
