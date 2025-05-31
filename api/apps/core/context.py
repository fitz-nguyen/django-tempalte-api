from apps.core import utils
from django.utils.deprecation import MiddlewareMixin

logger = utils.get_logger(__name__)


class AppContext(object):
    """
    A singleton object to scrape META data from HTTP Request Header

    usage:
    ip_address = AppContext.instance().ip_address
    app_version = AppContext.instance().app_version

    """

    __instance = None

    def __init__(self):
        if AppContext.__instance is not None:
            return
        self._user = None
        self._ip_address = None
        self._app_version = None
        self._is_ios = False
        self._is_android = False
        self._platform = None
        self._device_id = None
        self._timezone = None
        self._platform_version = None

        AppContext.__instance = self

    @staticmethod
    def instance():
        if AppContext.__instance is None:
            AppContext()
        return AppContext.__instance

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, value):
        self._user = value

    @property
    def app_version(self):
        return self._app_version

    @app_version.setter
    def app_version(self, value):
        self._app_version = value

    @property
    def ip_address(self):
        return self._ip_address

    @ip_address.setter
    def ip_address(self, value):
        self._ip_address = value

    @property
    def is_ios(self):
        return self._is_ios

    @is_ios.setter
    def is_ios(self, value):
        self._is_ios = value

    @property
    def is_android(self):
        return self._is_android

    @is_android.setter
    def is_android(self, value):
        self._is_android = value

    @property
    def device_id(self):
        return self._device_id

    @device_id.setter
    def device_id(self, value):
        self._device_id = value

    @property
    def platform_version(self):
        return self._platform_version

    @platform_version.setter
    def platform_version(self, value):
        self._platform_version = value

    @property
    def platform(self):
        return self._platform

    @platform.setter
    def platform(self, value):
        self._platform = value


class AppContextMiddleware(MiddlewareMixin):
    def process_request(self, request):
        try:
            context = AppContext.instance()
            context.user = request.user
            context.app_version = utils.get_app_version(request=request)
            context.device_id = utils.get_device_id(request=request)
            context.platform = utils.get_platform(request=request)
            context.platform_version = utils.get_platform_version(request=request)
        except Exception as e:
            logger.info("===== Exception in set context ======")
            logger.info(e)
