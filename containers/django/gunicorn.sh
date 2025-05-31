#!/bin/sh
# migration
python /home/app/api/manage.py migrate

# build static assets
#python /home/app/api/manage.py collectstatic --noinput
python /home/app/api/run_receiver_trigger_from_postgresql.py

# start api with gunicorn
gunicorn config.wsgi -b 0.0.0.0:8000
