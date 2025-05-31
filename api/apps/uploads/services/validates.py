from apps.uploads.exceptions import FileNameOrFileTypeIsNotValidException, LargeFileException
from django.conf import settings

FILE_FORMATS = ["jpeg", "gif", "jpg", "png", "svg", "pdf"]


def validate_maximum_file_size(file_size: int):
    if file_size > settings.MAXIMUM_FILE_SIZE:
        raise LargeFileException()


def validate_content_type(content_type: str):
    file_types = content_type.split("/")
    if not content_type or len(file_types) < 2:
        raise FileNameOrFileTypeIsNotValidException()
    file_type = file_types[1]
    if file_type in FILE_FORMATS:
        return
    raise FileNameOrFileTypeIsNotValidException()
