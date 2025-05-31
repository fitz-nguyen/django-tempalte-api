#!/bin/bash

cd /usr/src/api
/usr/src/api/virtualenv/bin/celery -A apps.core beat
