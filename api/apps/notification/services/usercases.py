from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, List, Optional

from apps.notification import exceptions
from apps.notification.services import query
from apps.users.models import User


class UserCase(ABC):
    @abstractmethod
    def execute(self, **kwargs) -> Optional[Any]:
        pass


class YesNo(Enum):
    YES = "Y"
    NO = "N"


class MarkNotificationAsRead(UserCase):
    def __init__(self, user: User, ids: List[str], read_all: Optional[YesNo]):
        self.user = user
        self.ids = ids
        self.read_all = read_all

    def execute(self, **kwargs) -> Optional[Any]:
        if self.read_all != YesNo.YES.value and len(self.ids) == 0:
            raise exceptions.ReadNotificationIDsEmptyException()

        queryset = query.get_unread_messages_queryset(user=self.user)
        if self.read_all != YesNo.YES.value:
            queryset = queryset.filter(pk__in=self.ids)

        return queryset.update(read=True)


class ArchiveNotification(UserCase):
    def __init__(self, user: User, ids: List[str], archive_all: Optional[YesNo]):
        self.user = user
        self.ids = ids
        self.archive_all = archive_all

    def execute(self, **kwargs) -> Optional[Any]:
        if self.archive_all != YesNo.YES.value and len(self.ids) == 0:
            raise exceptions.ArchiveNotificationIDsEmptyException()
        queryset = query.get_visible_messages_queryset(user=self.user)
        if self.archive_all != YesNo.YES.value:
            queryset = queryset.filter(pk__in=self.ids)

        return queryset.delete()
