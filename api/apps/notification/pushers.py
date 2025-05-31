from abc import ABC, abstractmethod
from typing import Optional

from fcm_django.models import FCMDevice
from firebase_admin.messaging import AndroidConfig, APNSConfig, APNSPayload, Aps, Message, Notification

from apps.core.utils import get_logger
from apps.notification.services.message import NotificationMessage
from apps.notification.services.result import SendNotificationResult

logger = get_logger(__name__)


class Pusher(ABC):
    @abstractmethod
    def send(self, message: NotificationMessage, badge: Optional[int] = None) -> SendNotificationResult:
        raise NotImplementedError()


class FireBasePusher:
    @classmethod
    def get_user_devices(cls, user):
        if not user:
            return []
        return FCMDevice.objects.filter(user=user, active=True)

    def send(
        self, message: NotificationMessage, badge: Optional[int] = None, image: Optional[str] = None
    ) -> SendNotificationResult:
        user = message.user
        devices = self.get_user_devices(user)
        if not devices.exists():
            logger.debug(f"User {user} has no devices")
            return SendNotificationResult(success=False, error="ERROR: No devices")
        for device in devices:
            device.send_message(
                message=Message(
                    data=message.data,
                    notification=Notification(
                        title=message.title,
                        body=message.content,
                        image=image,
                    ),
                    apns=APNSConfig(
                        payload=APNSPayload(
                            aps=Aps(
                                badge=badge,
                                sound="default",
                            )
                        )
                    ),
                ),
            )
        return SendNotificationResult(success=True)

    def send_data_message(self, message: NotificationMessage):
        # TODO : refactor this code using user_id instead
        user = message.user
        devices = self.get_user_devices(user)
        for device in devices:
            device.send_message(
                message=Message(
                    data=message.data,
                    apns=APNSConfig(payload=APNSPayload(aps=Aps(content_available=True))),
                    android=AndroidConfig(priority="high"),
                ),
            )


class FakePusher(Pusher):
    def send(self, message: NotificationMessage, badge: Optional[int] = None) -> SendNotificationResult:
        logger.info(f"Fake Pusher: [{message.title}], [{message.content}], [{badge}]")
        return SendNotificationResult(True)
