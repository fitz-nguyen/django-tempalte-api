#!/bin/bash

echo "####################################"
echo "CREDENTIALS for environment: $ENVIRONMENT"
echo "####################################"

USERNAME="admin"
EMAIL="admin@admin.com"
PASSWORD=`date +%s | sha256sum | base64 | head -c 32 ; echo`
echo "DJANGO USERNAME=${USERNAME}"
echo "DJANGO EMAIL=${EMAIL}"
echo "DJANGO PASSWORD=${PASSWORD}"

cd /usr/src/api
. virtualenv/bin/activate
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.get(username='${USERNAME}', is_superuser=True).delete()" | python3 manage.py shell --settings=config.settings.$ENVIRONMENT
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('${USERNAME}', '${EMAIL}', '${PASSWORD}')" | python3 manage.py shell --settings=config.settings.$ENVIRONMENT
