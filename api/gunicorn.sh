#!/bin/sh

if [ -z ${ENVIRONMENT} ]; then export ENVIRONMENT=local; fi

# build static assets
python /usr/src/api/manage.py collectstatic --noinput --settings=config.settings.$ENVIRONMENT

#python /usr/src/api/receiver_trigger_from_postgresql.py


# start api with gunicorn
/usr/src/api/virtualenv/bin/gunicorn config.wsgi -b 0.0.0.0:8000 --chdir=/usr/src/api --workers=5 --timeout=1200
