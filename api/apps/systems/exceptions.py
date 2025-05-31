from apps.core.exceptions import GenericException


class SystemConfigNotSetException(GenericException):
    code = 5501
    verbose = True

    def __init__(self, message=None):
        if not message:
            message = "Please contact the admin."
        super().__init__(message=message)
