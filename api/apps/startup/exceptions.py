from apps.core.exceptions import GenericException


class PlatformNotFoundException(GenericException):
    code = 11000
    verbose = True

    def __init__(self, message=None):
        if not message:
            message = "Not found platform"
        super().__init__(message=message)
