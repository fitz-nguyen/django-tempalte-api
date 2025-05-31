#!/bin/bash

echo "Remove celery beat id"
sudo rm -Rf /usr/src/api/celerybeat.pid
sudo rm -Rf /usr/src/api/celerybeat-schedule

if [ "$ENVIRONMENT" == "local" ]; then
    cd /usr/src/api && source virtualenv/bin/activate && python3 manage.py runserver 0.0.0.0:8000
else
#    echo " -- Restarting Nginx --"
#    sudo service nginx stop
#    sudo service nginx start
#    echo "Done!"

    echo " -- Restarting Supervisord --"
    sudo service supervisor stop
    sudo pkill -9 celery
    sudo pkill -9 celerybeat
    sudo service supervisor start
    echo "Done!"
fi
