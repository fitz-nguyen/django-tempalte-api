#!/bin/bash

echo "####################################"
echo "MIGRATE for environment: $ENVIRONMENT"
echo "####################################"

cd /usr/src/api
. virtualenv/bin/activate
python3 manage.py migrate --settings=config.settings.$ENVIRONMENT
