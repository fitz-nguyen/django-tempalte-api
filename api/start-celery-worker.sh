#!/bin/bash

cd /usr/src/api
/usr/src/api/virtualenv/bin/celery -A apps.core worker -P gevent -c 2 --prefetch-multiplier=1


