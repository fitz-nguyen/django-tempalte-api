#!/bin/bash

echo "####################################"
echo "SEEDS for environment: $ENVIRONMENT"
echo "####################################"

cd /usr/src/api
. virtualenv/bin/activate


python3 manage.py update_dashboard_lead_indexes --settings=config.settings.$ENVIRONMENT
python3 manage.py add_sale_representative_name --settings=config.settings.$ENVIRONMENT
python3 manage.py add_most_recent_permit --settings=config.settings.$ENVIRONMENT