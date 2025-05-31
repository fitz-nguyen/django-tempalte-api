#!/bin/sh

echo ""
echo "#########################"
echo "# DJANGO SETTINGS FOR ${ENVIRONMENT}"
echo "# Frontend URL: ${FRONTEND_BASE_URL}" #http://localhost
echo "# Backend URL: ${BASE_URL}"
echo "#########################"
echo ""

# EC2
elbDNSName=`echo secrets/${ENVIRONMENT}/terraform/output/elb_dns_name.json`
if [[ "$ENVIRONMENT" != "development" && "$BASE_URL" = "http://localhost" ]]; then
    BASE_URL="http://${elbDNSName}"
    FRONTEND_BASE_URL="http://${elbDNSName}"
fi

# DATABASE
dbAddress=`cat secrets/${ENVIRONMENT}/terraform/output/address.json | sed 's/"//g'`
dbUsername=`cat secrets/${ENVIRONMENT}/terraform/output/username.json | sed 's/"//g'`
dbPassword=`cat secrets/${ENVIRONMENT}/terraform/output/password.json | sed 's/"//g'`
dbDatabase=`cat secrets/${ENVIRONMENT}/terraform/output/database.json | sed 's/"//g'`
DATABASE_URL='postgres://'$dbUsername':'$dbPassword'@'$dbAddress'/'$dbDatabase
#echo "${DATABASE_URL}"

# REDIS
#cacheNode=`jq -r ".value" secrets/${ENVIRONMENT}/terraform/output/cache_nodes.json`
#cacheAddress=`echo $cacheNode | jq -r ".[0].address"`
#cachePort=`echo $cacheNode | jq -r ".[0].port"`
REDIS_CONN_URL='redis://localhost:6379'
CELERY_BROKER_URL='redis://localhost:6379'
#echo "${REDIS_CONN_URL}"

rm -Rf secrets/${ENVIRONMENT}/django/settings/.env.${ENVIRONMENT}
cp -Rf secrets/${ENVIRONMENT}/django/settings/.env.template secrets/${ENVIRONMENT}/django/settings/.env.${ENVIRONMENT}

if [[ "$ENVIRONMENT" != "development" ]]; then
    sed 's|DJANGO_DEBUG=True|DJANGO_DEBUG=False|g' secrets/${ENVIRONMENT}/django/settings/.env.${ENVIRONMENT} > newfile; mv newfile secrets/${ENVIRONMENT}/django/settings/.env.${ENVIRONMENT}
    sed 's|DEBUG=True|DEBUG=False|g' secrets/${ENVIRONMENT}/django/settings/.env.${ENVIRONMENT} > newfile; mv newfile secrets/${ENVIRONMENT}/django/settings/.env.${ENVIRONMENT}
fi
sed 's|${ENVIRONMENT}|'"${ENVIRONMENT}"'|g' secrets/${ENVIRONMENT}/django/settings/.env.${ENVIRONMENT} > newfile; mv newfile secrets/${ENVIRONMENT}/django/settings/.env.${ENVIRONMENT}
sed 's|${DATABASE_URL}|'"${DATABASE_URL}"'|g' secrets/${ENVIRONMENT}/django/settings/.env.${ENVIRONMENT} > newfile; mv newfile secrets/${ENVIRONMENT}/django/settings/.env.${ENVIRONMENT}
sed 's|${REDIS_CONN_URL}|'"${REDIS_CONN_URL}"'|g' secrets/${ENVIRONMENT}/django/settings/.env.${ENVIRONMENT} > newfile; mv newfile secrets/${ENVIRONMENT}/django/settings/.env.${ENVIRONMENT}
sed 's|${CELERY_BROKER_URL}|'"${CELERY_BROKER_URL}"'|g' secrets/${ENVIRONMENT}/django/settings/.env.${ENVIRONMENT} > newfile; mv newfile secrets/${ENVIRONMENT}/django/settings/.env.${ENVIRONMENT}
sed 's|${BASE_URL}|'"${BASE_URL}"'|g' secrets/${ENV}/django/settings/.env.${EENVIRONMENTNV} > newfile; mv newfile secrets/${ENVIRONMENT}/django/settings/.env.${ENVIRONMENT}
sed 's|${FRONTEND_BASE_URL}|'"${FRONTEND_BASE_URL}"'|g' secrets/${ENVIRONMENT}/django/settings/.env.${ENVIRONMENT} > newfile; mv newfile secrets/${ENVIRONMENT}/django/settings/.env.${ENVIRONMENT}
