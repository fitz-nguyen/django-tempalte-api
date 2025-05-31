from apps.core.exceptions import GenericException, InvalidDataException, ParseJsonErrorException, UnauthorizedException
from apps.core.utils import get_logger
from django.core.exceptions import ValidationError as ValidationError_Core
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated, ParseError, ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = get_logger(__name__)


def response_error(ex, status_code=400):
    if not isinstance(ex, GenericException):
        if isinstance(ex, ValidationError_Core) and hasattr(ex, "code") and ex.code == "invalid":
            ex = InvalidDataException(message=ex.messages[0], status_code=400)
            return Response(data=ex.serialize(), status=status.HTTP_400_BAD_REQUEST)
        ex = GenericException(message=str(ex), status_code=status_code)
    error_message = "Oops! Something went wrong, please try again."
    if ex.verbose is True:
        error_message = str(ex)

    error_data = {
        "code": ex.code,
        "message": error_message,
        "summary": ex.summary,
        "status_code": status_code,
    }
    return Response(data=error_data, status=ex.status_code)


def try_parse_validation_error(exc: Exception) -> GenericException:
    if isinstance(exc, NotAuthenticated):
        return UnauthorizedException()

    if isinstance(exc, ValidationError):
        field = list(exc.detail.keys())[0]
        error = exc.detail.get(field)[0]
        error_detail = str(error)
        code = error.code
        return InvalidDataException(field=field, error_detail=error_detail, code=code)
    elif isinstance(exc, ParseError):
        return ParseJsonErrorException(message=str(exc.detail))
    elif isinstance(exc, GenericException):
        return exc
    return GenericException(str(exc))


def api_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    logger.exception(exc)

    response = exception_handler(exc, context)
    # Handle Error of 500
    if not response:
        return response_error(exc)

    # Parse Generic Exception
    ex = try_parse_validation_error(exc)
    response.data = ex.serialize()
    return response
