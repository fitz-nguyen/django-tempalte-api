from typing import Any, List
from urllib.parse import urlparse

from apps.core.utils import get_logger
from django.conf import settings
from socket_io_emitter import Emitter

logger = get_logger(__name__)


class PubSubEmitter:
    def emit(self, event: str, payload: Any):
        raise NotImplementedError()

    def broadcast(self, event: str, payload: Any):
        raise NotImplementedError()

    def of(self, nsp: str):
        raise NotImplementedError()

    def to(self, rooms: List[str]):
        raise NotImplementedError()


class SocketIOEmitter(PubSubEmitter):
    __instance = None
    _emitter = None

    def __init__(self):
        if SocketIOEmitter.__instance is not None:
            return
        SocketIOEmitter.__instance = self
        self.__rooms = []

    @staticmethod
    def instance():
        if SocketIOEmitter.__instance is None:
            SocketIOEmitter()
        return SocketIOEmitter.__instance

    @property
    def emitter(self):
        if self._emitter:
            return self._emitter
        try:
            urls = urlparse(settings.REDIS_CONN_URL)
            key = settings.SOCKET_IO_EMITTER_KEY

            opts = dict(
                host=urls.hostname,
                port=urls.port,
                password=urls.password,
                key=key,
            )
            self._emitter = Emitter(opts)

            return self._emitter
        except Exception as e:
            logger.debug("Failed to initialize Emitter instance %s" % str(e))
            raise e

    def emit(self, event: str, payload: Any):
        """

        :param event: message string
        :param payload: dict of payload
        :return: void
        """
        try:
            for room in self.__rooms:
                self.emitter.To(room).Emit(event, payload)
            self.__rooms = []
        except Exception as e:
            logger.exception(e)

    def broadcast(self, event: str, payload: Any):
        self.emitter.Emit(event, payload)

    def of(self, nsp: str) -> PubSubEmitter:
        self.emitter.Of(nsp)
        return self

    def to(self, rooms: List[str]) -> PubSubEmitter:
        self.__rooms = rooms
        return self
