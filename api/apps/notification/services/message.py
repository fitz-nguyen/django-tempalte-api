from typing import Optional

from apps.core.utils import get_logger

logger = get_logger(__name__)


class NotificationMessage:
    @property
    def user(self):
        raise NotImplementedError()

    @property
    def actor(self):
        return None

    @property
    def verb(self) -> str:
        raise NotImplementedError()

    @property
    def title(self) -> str:
        raise NotImplementedError()

    @property
    def content(self) -> str:
        raise NotImplementedError()

    @property
    def template(self) -> Optional[str]:
        return None

    @property
    def payload(self) -> Optional[dict]:
        return None

    @property
    def content_object(self):
        return None

    @property
    def target_object(self):
        return None

    @property
    def visible(self) -> bool:
        return True

    @property
    def is_persistent(self) -> bool:
        return True

    @property
    def data(self) -> Optional[dict]:
        """
        Extra payload for FCM
        :return:
        """
        return None

    @property
    def meta(self) -> Optional[dict]:
        """
        meta info
        """
        return None
