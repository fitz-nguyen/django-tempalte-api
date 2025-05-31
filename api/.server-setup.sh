#!/bin/bash


echo "####################################"
echo "environment: $ENVIRONMENT"
echo "####################################"

mkdir /usr/src/dist -p

sudo apt update -y
sudo apt upgrade -y
sudo apt install apt-utils python3-psycopg2 sudo build-essential libmysqlclient-dev git curl zip unzip -y
curl -sL https://deb.nodesource.com/setup_10.x | sudo -E bash -
sudo apt install nginx -y
sudo apt update -y
sudo apt install supervisor python3-pip -y
sudo apt install python3-virtualenv -y
sudo apt install gdal-bin libgdal-dev -y

mkdir /usr/src/api_staticfiles
mkdir /usr/src/api_media

openssl genrsa -out jwt_api_key 1024
openssl rsa -in jwt_api_key -pubout -out jwt_api_key.pub
sudo mv jwt_api_key /jwt_api_key
sudo mv jwt_api_key.pub /jwt_api_key.pub

# start nginx on start up
update-rc.d nginx enable
