from abc import ABC, abstractmethod
from typing import Optional

from apps.core.utils import get_logger
from apps.notification.pushers import Pusher
from apps.notification.services.message import NotificationMessage
from apps.notification.services.result import SendNotificationResult
from apps.notification.settings import app_settings

logger = get_logger(__name__)


class Transport(ABC):
    @abstractmethod
    def send(self, message: NotificationMessage, badge: Optional[int] = None) -> SendNotificationResult:
        raise NotImplementedError()


class PushTransport(Transport):
    @classmethod
    def get_pusher(cls) -> Optional[Pusher]:
        pusher_class = app_settings.DEFAULT_PUSHER_CLASS
        logger.debug("Pusher Class: {}".format(pusher_class))
        if not pusher_class:
            return None
        return pusher_class()

    def send(self, message: NotificationMessage, badge: Optional[int] = None) -> SendNotificationResult:
        pusher = self.get_pusher()
        if not pusher:
            return SendNotificationResult(success=False, error="Missed Pusher Class")
        return pusher.send(message, badge=badge)


class MailerTransport(Transport):
    @abstractmethod
    def send(self, message: NotificationMessage, badge: Optional[int] = None) -> SendNotificationResult:
        pass
