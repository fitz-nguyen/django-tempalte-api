from urllib.parse import urlparse

import redis
from django.conf import settings


def get_redis(db=0) -> redis.Redis:
    urls = urlparse(settings.REDIS_CONN_URL)
    return redis.Redis(host=urls.hostname, port=urls.port, db=db, password=urls.password)
