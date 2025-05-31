import os  # noqa
import socket

from .common import *
from .common import INSTALLED_APPS, MIDDLEWARE, TEMPLATES, env

# DEBUG
# ------------------------------------------------------------------------------
DEBUG = env.bool("DJANGO_DEBUG", default=True)
TEMPLATES[0]["OPTIONS"]["debug"] = DEBUG
ALLOWED_HOSTS = ["*"]


# django-debug-toolbar
# ------------------------------------------------------------------------------
INSTALLED_APPS += ("debug_toolbar",)
MIDDLEWARE += ("debug_toolbar.middleware.DebugToolbarMiddleware",)

INTERNAL_IPS = [
    "127.0.0.1",
    "10.0.2.2",
]
# tricks to have debug toolbar when developing with docker
if os.environ.get("USE_DOCKER") == "yes":
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        INTERNAL_IPS += [ip[:-1] + "1"]
    except (socket.gaierror, socket.herror):
        # If we can't resolve the hostname, just use localhost
        INTERNAL_IPS += ["127.0.0.1"]

# django-extensions & nose test
# ------------------------------------------------------------------------------
INSTALLED_APPS += ("django_extensions",)
