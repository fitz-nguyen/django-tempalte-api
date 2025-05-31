#!/bin/sh

if [ -z ${ENVIRONMENT} ]; then export ENVIRONMENT=local; fi
if [ -z ${DATABASE_URL} ]; then export DATABASE_URL="postgres://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}"; fi

python manage.py migrate
python manage.py collectstatic --noinput
python receiver_trigger_from_postgresql
python manage.py runserver 0.0.0.0:8000 --settings=config.settings.$ENVIRONMENT

