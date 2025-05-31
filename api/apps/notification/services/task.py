from apps.core.utils import logger
from apps.notification.services.notifier import Notifier
from apps.notification.services.storage import NotificationStorage, QueuedNotificationMessage


def send_notification_task_handler(message_id: str):
    try:
        message = NotificationStorage.load(message_id=message_id)
        if not message or not message.is_queued():
            logger.warning(f"Message ID not found: {message_id}")
            return
        queued_message = QueuedNotificationMessage(message=message)
        result = Notifier.send(message=queued_message)
        NotificationStorage.update_status(message=message, success=result.is_success(), error=result.error)
    except Exception as ex:
        logger.exception(ex)
