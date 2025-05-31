from .common import *  # noqa
from .common import env

DEBUG = env.bool("DEBUG", default=False)

SECRET_KEY = env("DJANGO_SECRET_KEY")

# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default="*")
