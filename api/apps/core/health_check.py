from celery.exceptions import TaskRevokedError
from django.conf import settings
from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import ServiceReturnedUnexpectedResult, ServiceUnavailable

from apps.core.tasks import add


class CheckCeleryResult(BaseHealthCheckBackend):
    #: The status endpoints will respond with a 200 status code
    #: even if the check errors.
    critical_service = False

    def check_status(self):
        timeout = getattr(settings, "HEALTHCHECK_CELERY_RESULT_TIMEOUT", 10)
        result_timeout = getattr(settings, "HEALTHCHECK_CELERY_RESULT_TIMEOUT", timeout)
        queue_timeout = getattr(settings, "HEALTHCHECK_CELERY_RESULT_TIMEOUT", timeout)

        try:
            result = add.apply_async(args=[4, 4], expires=queue_timeout, result_extended=True, ignore_result=False)
            result.get(timeout=result_timeout)
            if result.status != "SUCCESS":
                self.add_error(ServiceReturnedUnexpectedResult("Celery returned wrong result"))
        except IOError as e:
            self.add_error(ServiceUnavailable("IOError"), e)
        except NotImplementedError as e:
            self.add_error(
                ServiceUnavailable("NotImplementedError: Make sure CELERY_RESULT_BACKEND is set"),
                e,
            )
        except TaskRevokedError as e:
            self.add_error(
                ServiceUnavailable(
                    "TaskRevokedError: The task was revoked, likely because it spent " "too long in the queue"
                ),
                e,
            )
        except TimeoutError as e:
            self.add_error(
                ServiceUnavailable("TimeoutError: The task took too long to return a result"),
                e,
            )
        except BaseException as e:
            self.add_error(ServiceUnavailable("Unknown error"), e)

    def identifier(self):
        return self.__class__.__name__  # Display name on the endpoint.
