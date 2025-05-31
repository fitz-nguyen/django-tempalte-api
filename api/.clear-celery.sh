#!/bin/bash
    echo " -- Restarting Supervisord --"
    sudo service supervisor stop
    sudo pkill -9 celery
    sudo pkill -9 celerybeat
    sudo service supervisor start
    echo "Done!"
fi
