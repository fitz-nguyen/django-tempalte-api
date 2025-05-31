#!/bin/bash

echo "####################################"
echo "POST DEPLOY for environment: $ENVIRONMENT"
echo "####################################"

# create api soft link
sudo ln -s /usr/src/app/api /usr/src/api

cd /usr/src/app
# copy configs
#sudo cp ./containers/nginx/conf.d/api.conf /etc/nginx/conf.d/api.conf
#sudo cp ./containers/nginx/sites-enabled/default /etc/nginx/sites-enabled/default
sudo cp ./api/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

cd /usr/src/api
sudo sed 's/config.settings.local/config.settings.'"$ENVIRONMENT"'/g' config/wsgi.py > changed.txt && mv changed.txt config/wsgi.py
sudo sed 's/config.settings.local/config.settings.'"$ENVIRONMENT"'/g' gunicorn.sh > changed.txt && mv changed.txt gunicorn.sh
sudo sed 's/config.settings.local/config.settings.'"$ENVIRONMENT"'/g' apps/core/celery.py > changed.txt && mv changed.txt apps/core/celery.py

sudo chmod +x ./.ci-post-deploy.sh
sudo chmod +x ./.server-setup.sh
sudo chmod +x ./.start-services.sh
sudo chmod +x ./gunicorn.sh
sudo chmod +x ./start-celery-beat.sh
sudo chmod +x ./start-celery-worker.sh
sudo chmod +x ./.setup-db.sh
sudo chmod +x ./.setup-db-seeds.sh
sudo chmod +x ./.setup-api-credentials.sh

# set up media and static asset links
ln -s /usr/src/api_media/ media
ln -s /usr/src/api_staticfiles/ staticfiles

# alias and use python3 and set up virtual environment
alias python=python3.12
virtualenv --python=/usr/bin/python3.12 virtualenv
. virtualenv/bin/activate
pip3 install -r requirements/$ENVIRONMENT.txt
sudo rm -Rf staticfiles
python3 ./manage.py collectstatic --settings=config.settings.$ENVIRONMENT --noinput
