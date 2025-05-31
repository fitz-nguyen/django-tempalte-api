#!/bin/sh

# terraform sync
PROVIDER=${PROVIDER:=aws} mkdir -p secrets/${ENVIRONMENT}/terraform; cp -af hosting/terraform/environments/${ENVIRONMENT}/aws/*.json secrets/${ENVIRONMENT}/terraform/environments

# django sync
PROVIDER=${PROVIDER:=aws} mkdir -p secrets/${ENVIRONMENT}/django; cp -af api/config/settings secrets/${ENVIRONMENT}/django
