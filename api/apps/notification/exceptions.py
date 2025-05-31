from apps.core.exceptions import GenericException


class ReadNotificationIDsEmptyException(GenericException):
    code = 5000
    verbose = True

    def __init__(self, message=None):
        if not message:
            message = "Notification ID list to mark as read is empty."
        super().__init__(message=message)


class ArchiveNotificationIDsEmptyException(GenericException):
    code = 5001
    verbose = True

    def __init__(self, message=None):
        if not message:
            message = "Notification ID list to archive is empty."
        super().__init__(message=message)
