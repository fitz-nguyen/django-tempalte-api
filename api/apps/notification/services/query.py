from django.db.models.manager import QuerySet

from apps.notification import choices
from apps.notification.models import Message
from apps.users.models import User


def get_visible_messages_queryset(user: User) -> QuerySet:
    queryset = Message.objects.select_related("category").filter(user=user, visible=True).order_by("-created")

    return queryset


def get_unread_messages_queryset(user: User) -> QuerySet:
    queryset = Message.objects.filter(user=user, visible=True, read=False, status=choices.MESSAGE_STATUS_SENT)

    return queryset
