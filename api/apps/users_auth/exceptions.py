from apps.core.exceptions import GenericException


class TokenExpiredException(GenericException):
    code = 8000
    verbose = True

    def __init__(self, message=None):
        if not message:
            message = "Token is invalid or expired."
        super().__init__(message=message)


class PermissionIsNotValidException(GenericException):
    code = 8001
    verbose = True

    def __init__(self, message=None):
        if not message:
            message = "You don't have permission to log in to this app. Please connect to admin."
        super().__init__(message=message)


class EmailIsNotValidException(GenericException):
    code = 8000
    verbose = True

    def __init__(self, message=None):
        if not message:
            message = "The email is not valid."
        super().__init__(message=message)


class EmailConfirmationIsNotValidException(GenericException):
    code = 8888
    verbose = True

    def __init__(self, message=None):
        if not message:
            message = "The email confirmation link is expired."
        super().__init__(message=message)


class UserIsNotActiveException(GenericException):
    code = 8889
    verbose = True

    def __init__(self, message=None):
        if not message:
            message = "Your account is inactive. Please contact the admin for support"
        super().__init__(message=message)


class UserIsNotApprovedException(GenericException):
    code = 8890
    verbose = True

    def __init__(self, message=None):
        if not message:
            message = "Your account has not been approved. Please contact the admin for support"
        super().__init__(message=message)


class CompanyIsNotActiveException(GenericException):
    code = 8891
    verbose = True

    def __init__(self, message=None):
        if not message:
            message = "Your company has been suspended. Please contact the admin for support"
        super().__init__(message=message)
