# Django Template API

## Prerequisites
- Python 3.6 (Ignore if using Docker)
- Virtualenv (Ignore if using Docker)
- Postgres 9.6 + (Ignore if using Docker)
- Redis (Ignore if using Docker)
- Docker (Optional)
- Docker Compose (Optional)
- Postgris 1.0.4
- GDAL
## Setup Configuration Files

```bash
npm run setup:config

# Edit DATABASE_URL in ./config/settings/.env
DATABASE_URL=postgres://goldfish:123456@postgres:5432/goldfish

```

## Install Pre-commit Hooks
Pre-commit hooks are executed as soon as you commit code to reformat and validate PEP8 standard

```bash
pre-commit install

# Test hooks
pre-commit run --all-files
```


## virtualenv

```bash
# 1. Create virtual .env
cd api
python3 -m venv virtualenv
. virtualenv/bin/activate


# 2.1 Install Gdal
$ sudo apt-get install libgdal-dev gdal-bin
# On Window:
https://stackoverflow.com/questions/49139044/geodjango-on-windows-could-not-find-the-gdal-library-oserror-winerror-12/49159195#49159195

# 2. Install dependency
pip install -r requirements/local.txt

# 2.5 Enable PostGIS in your database
# For PostgreSQL, you need to enable the PostGIS extension:
$ sudo -u postgres psql -c "CREATE EXTENSION postgis;" -d your_database_name
# Without PostGIS extension enabled, spatial queries will fail

# 3. Migrate database
$ ./manage.py migrate

If enviroment not recognize posgris:
$ sudo apt install postgresql-10-postgis-scripts

# 3.1 Set up dashboard lead data table partitioning
# Create the parent table with proper partitioning structure
$ python manage.py create_dashboard_lead_data_table

# Update indexes for existing company partition tables
$ python manage.py update_dashboard_lead_indexes
# Or for specific company:
$ python manage.py update_dashboard_lead_indexes --company_id=COMPANY_ID

#3.5 Set up data
python3 manage.py seed_chart_config

# 4. Start Django
$ ./manage.py runserver 0.0.0.0:8000
```
```text

For Window OS, you need to push these settings in common.py file to can using GDAL lib

if os.name == "nt":
    import platform

    OSGEO4W = r"C:\OSGeo4W"
    if "64" in platform.architecture()[0]:
        OSGEO4W += "64"
    assert os.path.isdir(OSGEO4W), "Directory does not exist: " + OSGEO4W
    os.environ["OSGEO4W_ROOT"] = OSGEO4W
    os.environ["GDAL_DATA"] = OSGEO4W + r"\share\gdal"
    os.environ["PROJ_LIB"] = OSGEO4W + r"\share\proj"
    os.environ["PATH"] = OSGEO4W + r"\bin;" + os.environ["PATH"]
```

## Build and Start App using Docker
```bash

# Set environment (optional) default=local
$ ENVIRONMENT=development npm run docker:build

# Start container
$ npm run docker:up

# Stop container
$ npm run docker:down

# SSH to api container
$ npm run docker:exec:api
```

## Initiate data
```bash
# 1. SSH to docker container
npm run docker:exec:api:createsuperuser
# 2. Enter email, username, password
```

```bash
# 3. make migrations
npm run docker:exec:api:db:makemigrations
```

```bash
# 4. run migrations
npm run docker:exec:api:db:migrate
```

## Health check
```bash
To show main page of django-health-check library (html) use:

http://localhost:8000/ht/status/
```
```bash
To show checks status in json format use:

http://localhost:8000/ht/status?format=json
```
```bash
To show status of one check named 'mycheck' in json format use:

http://myserver/status?format=json&checks=mycheck

These name check is available: db','cache', 'celery','storage'
```
```bash
To show status of some checks (mycheck1 and mycheck2) in json format use:

http://myserver/status?format=json&checks=mycheck1,mycheck2
```
```
HTTP status code:

200: If all queried checks are in status OK.
500: If any queried check is WRONG.
```

## Create Localization
https://docs.djangoproject.com/en/3.0/topics/i18n/#term-translation-string
```bash
# 1. create localization
npm run docker:exec:api:create:locale
```

```bash
# 2. compile localization
npm run docker:exec:api:compile:locale
```
### Coverage
```bash

# Virtualenv
source  ./virtualenv/bin/activate
coverage run --source=apps manage.py test apps

```
## Django Admin
- URL: http://localhost/admin

## Swagger Document
- URL: http://localhost/docs

## API Authentication
- Both OAuth2 and Auth Token are supported

## Create OAuth2 Application
- Login to Django Admin
- Click Application to create new application
    + Choose an User
    + Client type: public
    + Authorization Grant type: Resource owner password-based
    + Enter application name
    + Save

## Oauth2 API
- URL: http://localhost:8000/v1/o/token/
- Method: POST
- Example

<img src="api/docs/images/oauth2.png">


## Create new App

```bash
# 1. SSH to API Container
$ docker-compose exec api bash

# 2. Create new app folder
$ mkdir -p apps/[APP_NAME]

# 3. Create new app
$ ./manage.py startapp [APP_NAME] apps/[APP_NAME]

# 4. Update your app name in app config in app/[APP_NAME]/apps.py

name = 'apps.[APP_NAME]'
```

## Install new app

```python
# 5. Add new app in config/settings/common
LOCAL_APPS = (
    'apps.core.apps.CoreConfig',
    'apps.users.apps.UserConfig',
    'apps.APP_NAME',
)

```
## Best Practices
- separate into multiple small apps
- Avoid cycle dependency
- Should use UUID for Primary Key

Example

```python
import uuid

from django.db import models

user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
```

## Environment Terraform Setup (AWS)
Make sure you have your AWS credentials handy and add them to your aws/credentials file https://docs.aws.amazon.com/sdk-for-java/v1/developer-guide/setup-credentials.html. I suggest creating new profiles for each customer. Below is an example:

```
[project_a]
aws_access_key_id = your_access_key_id
aws_secret_access_key = your_secret_access_key
```

You'll also want to make sure you export the profile name prior to running terraform
```
export AWS_PROFILE=project_a
```

Explore the /hosting/terraform/src/{cloud}/example.backend.json and /hosting/terraform/src/{cloud}/example.json files for configuration variables. In order to update production, you must have a respective environment file. For example, you would have a production.json an production.backend.json file for production variables. There are development, staging, production environment available. Please contact your administrator for production values.

Create an S3 bucket that follows this format. Make sure you place the bucket in the same region your credentials is set to.:
`${config.account_id}.${config.region}.tfstates`

Terraform is set up to store its state in AWS's S3 bucket rather than on the local environment. This is ideal.

Copy the hosting/terraform/example.json and hosting/terraform/example.backend.json files and rename them to their appropriate environents. for example
- development.json
- staging.json
- production.json
Then fill in the required information. Terraform will refer to these to understand what needs to be done within the clound environment

Create an environment Key Pair within AWS and backup the pem files. For example: development, production, etc

Specify the environment you want to build for. `development` as default
```export ENVIRONMENT=development```

Follow the below steps to create the environment on ec2:
```npm run tf:aws:deploy```

Follow the below steps to create the environment on fargate:
```npm run tf:aws:deploy:fargate```

Follow the below steps to apply changes for a specific service:
```npm run tf:aws:apply:service -- --services=list_of_services```

Follow the below steps to destroy the environment:
```npm run tf:aws:destroy```

## Environment Terraform Setup (Azure)
Log into azure using "az" cli

Specify the environment you want to build for. `development` as default
```export ENVIRONMENT=development```

Follow the below steps to create the environemnt:
```npm run tf:azure:deploy```

Follow the below steps to destroy the environemnt:
```npm run tf:azure:destroy```

## Resources
[Terraform / ECS / Fargate / CI](https://github.com/tmknom/terraform-aws-ecs-fargate)

## Secrets folder
There is a "secrets" folder that's created when running the Terraform IaC scripts. This is used for a few reasons. But the main reason is to hold the terraform output variables to assist with building out the CI and Django environment variables.

## Create Django environment settings
To prepare the Gitlabs CI, you will need to have access to the infrastructure variables generated by Terraform (IaC).

The api/config/settings/.env.template is used to help create the environment files.

Files environment files are stored both in the api/config/settings/ folder as well as the /secrets folder.
```
ENVIRONMENT=${ENVIRONMENT} npm run api:settings:setup
ENVIRONMENT=${ENVIRONMENT} npm run creds:save
```

## Gitlabs CI/CD
To prepare the Gitlabs CI, you will need to have access to the infrastructure variables generated by Terraform (IaC).

Run the following steps to help set up Gitlabs:
1. Run the "Deploy the terraform environment" steps
2. Run the "Create Django environment settings" steps
```
ENVIRONMENT=${ENVIRONMENT} GITLABS_ACCESS_TOKEN=${GITLABS_ACCESS_TOKEN} GITLAB_PROJECT_ID=${GITLAB_PROJECT_ID} npm run pipeline:setup
```
