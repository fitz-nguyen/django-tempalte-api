from typing import Iterable, Optional

from apps.core.utils import get_logger
from apps.notification.models import Message
from apps.notification.services.message import NotificationMessage

logger = get_logger(__name__)


class QueuedNotificationMessage(NotificationMessage):
    def __init__(self, message: Message):
        self.message = message

    @property
    def user(self):
        return self.message.user

    @property
    def actor(self):
        return self.message.actor

    @property
    def verb(self) -> str:
        return self.message.verb

    @property
    def title(self) -> str:
        return self.message.title

    @property
    def content(self) -> str:
        return self.message.content

    @property
    def template(self) -> Optional[str]:
        return self.message.template

    @property
    def payload(self) -> Optional[dict]:
        return None

    @property
    def visible(self) -> bool:
        return self.message.visible

    @property
    def is_persistent(self) -> bool:
        return True


class NotificationStorage:
    @classmethod
    def load(cls, message_id: str) -> Optional[Message]:
        return Message.objects.filter(pk=message_id).first()

    @classmethod
    def get_badge(cls, message: NotificationMessage):
        user = message.user
        return Message.objects.filter(visible=True, read=False, user=user).count()

    @classmethod
    def create(cls, message: NotificationMessage) -> Message:
        """
        Create and push message in queued status
        :param message: NotificationMessage
        :return:
        """
        instance = cls.__init_instance(message)
        instance.save()
        return instance

    @classmethod
    def bulk_create(cls, messages: Iterable[NotificationMessage]) -> Iterable[Message]:
        """
        Create and push message in queued status
        :param messages: Iterable[NotificationMessage]
        :return:
        """
        instances = []
        for message in messages:
            instance = cls.__init_instance(message)
            instances.append(instance)
        return Message.objects.bulk_create(instances)

    @classmethod
    def __init_instance(cls, message: NotificationMessage):
        instance = Message(
            actor=message.actor,
            user=message.user,
            verb=message.verb,
            title=message.title,
            content=message.content,
            template=message.template,
            visible=message.visible,
            read=False,
            payload=message.payload,
            meta=message.meta,
        )
        return instance

    @classmethod
    def done(cls, message: Message):
        message.mark_as_sent()

    @classmethod
    def fails(cls, message: Message, error: Optional[str] = None):
        message.mark_as_failed(error=error)

    @classmethod
    def update_status(cls, message: Message, success=True, error: Optional[str] = None):
        if success:
            cls.done(message)
        else:
            cls.fails(message, error=error)
