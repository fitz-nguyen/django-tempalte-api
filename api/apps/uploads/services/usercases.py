import os
from typing import Iterable, List, Optional, Tuple

from apps.uploads.exceptions import FilePathDoesNotExistException
from apps.uploads.models import UploadFile
from apps.uploads.settings import app_settings
from apps.uploads.signals import dispatch_create_thumbnail, dispatch_mark_file_deleted, dispatch_mark_file_used
from apps.users.models import User
from django.conf import settings
from django.core.files.storage import default_storage
from django.db.models import Q
from sorl.thumbnail import get_thumbnail


class UploadFileService:
    def __init__(self, user: Optional[User]):
        self.user = user  # type: User

    @classmethod
    def get_upload_class(cls):
        upload_class = app_settings.UPLOAD_CLASS
        if not upload_class:
            return None
        return upload_class()

    @classmethod
    def get_public_url(cls, file_path):
        upload_class = cls.get_upload_class()
        return upload_class.generate_public_url(file_path)

    @classmethod
    def get_pre_signed_url(cls, request):
        upload_class = cls.get_upload_class()
        return upload_class.get_pre_signed_url(request)

    @classmethod
    def get_file(cls, file_path: str, file_id: str = None) -> Optional[UploadFile]:
        upload_file = UploadFile.objects.filter(Q(pk=file_id) | Q(file_path=file_path)).select_related("user").first()
        if upload_file:
            return upload_file
        return None

    def get_uploaded_files(self, file_paths: List[str]) -> Iterable[UploadFile]:
        return UploadFile.objects.filter(file_path__in=file_paths, user=self.user).select_related("user")

    def mark_file_used(self, file_path: str, file_id: str = None):
        upload_file = self.get_file(file_path=file_path, file_id=file_id)
        if not upload_file or not upload_file.is_new():
            return None
        upload_file.mark_as_used()
        dispatch_mark_file_used.send(sender=UploadFileService, uploaded_file=upload_file)
        return upload_file

    def delete(self, file_path: str, file_id: str = None):
        upload_file = self.get_file(file_path=file_path, file_id=file_id)
        if not upload_file:
            return
        default_storage.delete(str(upload_file.file_path))
        if upload_file.thumbnail_path:
            path_thumbnail = upload_file.thumbnail_path.values()
            for path in path_thumbnail:
                default_storage.delete(path)
        upload_file.mark_as_deleted()
        dispatch_mark_file_deleted.send(sender=UploadFileService, uploaded_file=upload_file)

    def create_thumbnail(self, file_path: str, thumb_size: str):
        upload_file = self.get_file(file_path=file_path, file_id=None)
        if not upload_file:
            raise FilePathDoesNotExistException()
        location_file = settings.MEDIA_ROOT + "/" + str(file_path)
        file_abspath_path = location_file
        if not os.path.exists(file_abspath_path):
            raise FilePathDoesNotExistException()

        get_thumbnail(file_abspath_path, thumb_size, crop="center", quality=99)
        file_path_name, file_ext = os.path.splitext(file_path)
        output_path = file_path_name + "_" + thumb_size + ".png"
        upload_file_thumbnail = upload_file.thumbnail_path
        if upload_file_thumbnail is None:
            upload_file_thumbnail = {thumb_size: output_path}
        else:
            upload_file_thumbnail.update({thumb_size: output_path})

        upload_file.thumbnail_path = upload_file_thumbnail
        upload_file.save()
        dispatch_create_thumbnail.send(sender=UploadFileService, uploaded_file=upload_file)
        return upload_file_thumbnail
