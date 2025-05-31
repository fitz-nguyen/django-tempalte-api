from typing import Iterable

from celery import Task
from django.db import transaction

from apps.notification.models import Message
from apps.notification.services.message import NotificationMessage
from apps.notification.services.notifier import Notifier
from apps.notification.services.storage import NotificationStorage
from apps.notification.services.task import send_notification_task_handler


class SendQueuedMessageTask(Task):
    ignore_result = True

    def run(self, message_id: str, *args, **kwargs):
        send_notification_task_handler(message_id=message_id)


class NotificationManager:
    @classmethod
    def send(cls, message: NotificationMessage):
        stored_message = None
        if message.is_persistent:
            stored_message = NotificationStorage.create(message=message)

        result = Notifier.send(message=message)
        if stored_message:
            NotificationStorage.update_status(
                message=stored_message,
                success=result.is_success(),
                error=result.error,
            )

    @classmethod
    def send_async_bulk(cls, messages: Iterable[NotificationMessage]):
        persistent_messages = [message for message in messages if message.is_persistent]
        non_persistent_messages = [message for message in messages if not message.is_persistent]
        stored_messages = NotificationStorage.bulk_create(messages=persistent_messages)

        # Send queued messages
        for stored_message in stored_messages:
            cls.send_queued_message(message=stored_message)

        # Send non-queued messages
        for message in non_persistent_messages:
            Notifier.send(message=message)

    @classmethod
    def send_async(cls, message: NotificationMessage):
        instance = NotificationStorage.create(message)
        cls.send_queued_message(message=instance)

    @classmethod
    def send_queued_message(cls, message: Message):
        transaction.on_commit(lambda: SendQueuedMessageTask().delay(message_id=str(message.pk)))


class TestMessage(NotificationMessage):
    """
    This is a sample of Notification Message
    """

    def __init__(self, user):
        self._user = user

    @property
    def user(self):
        return self._user

    @property
    def title(self) -> str:
        return "Test Push"

    @property
    def content(self):
        return "Sample message for {}".format(self.user)

    @property
    def verb(self):
        return "notification.sample"
