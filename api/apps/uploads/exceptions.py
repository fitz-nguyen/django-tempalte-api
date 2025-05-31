from apps.core.exceptions import GenericException


class FolderNameEmptyException(GenericException):
    code = 9000
    verbose = True

    def __init__(self, message=None):
        if not message:
            message = "Folder name can not be empty."
        super().__init__(message=message)


class FilePathDoesNotExistException(GenericException):
    code = 9001
    verbose = True

    def __init__(self, message=None):
        if not message:
            message = "Input file path for create thumbnail does not exist"
        super().__init__(message=message)


class FileNameOrFileTypeIsNotValidException(GenericException):
    code = 9002
    verbose = True

    def __init__(self, message=None):
        if not message:
            message = "File name or file type is not valid.."
        super().__init__(message=message)


class MarkFileUsedIsNotValidException(GenericException):
    code = 9003
    verbose = True

    def __init__(self, message=None):
        if not message:
            message = "This file is marked used or You are not own this file"
        super().__init__(message=message)


class FileEmptyException(GenericException):
    code = 9004
    verbose = True

    def __init__(self, message=None):
        if not message:
            message = "File is not valid"
        super().__init__(message=message)


class LargeFileException(GenericException):
    code = 9005
    verbose = True

    def __init__(self, message=None):
        if not message:
            message = "File is too large"
        super().__init__(message=message)


class S3InvalidArgumentException(GenericException):
    code = 9006
    verbose = True

    def __init__(self, message=None):
        if not message:
            message = "S3 is invalid argument"
        super().__init__(message=message)
