App Users Auth
---

## Overview

This application is an implementation of User Authentication and integrate with DRF.
It supports Rest Auth Token, JWT and Oauth2.


## Prerequisites
* Python 3.12
* Django >= 5.1.1
* django-oauth-toolkit==3.0.1
* django-cors-headers==4.4.0
* django-rest-auth==7.0.0
* django-allauth==65.0.1
* djangorestframework_simplejwt==5.3.1
* cryptography==43.0.1

## Setup

Edit your `settings/common.py` file:

### Installed apps


```python

THIRD_PARTY_APPS = (
    # Auth
    'rest_framework.authtoken',
    'oauth2_provider',
    'dj_rest_auth',

    # Registration
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'dj_rest_auth.registration',
)

LOCAL_APPS = (
    # ...
    'apps.users_auth.apps.UsersAuthConfig'
    # ...
)
```

### Middleware

````python
MIDDLEWARE = [
    # ...
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'oauth2_provider.middleware.OAuth2TokenMiddleware',
]
````

### Config allauth module

https://django-allauth.readthedocs.io/en/latest/configuration.html

```python

# Registration
SITE_ID = 1
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD_EMAIL = "email"
ACCOUNT_AUTHENTICATION_METHOD_USERNAME = "username"
ACCOUNT_EMAIL_VERIFICATION_MANDATORY = "mandatory"


ACCOUNT_ADAPTER = 'apps.users_auth.adapter.AccountAdapter'
```

### Authentication backend

```python
AUTHENTICATION_BACKENDS = (
    'oauth2_provider.backends.OAuth2Backend',  # if Oauth2 is enabled
    # Uncomment following if you want to access the admin
    'django.contrib.auth.backends.ModelBackend'
)
```

### Rest Framework

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'apps.users_auth.authentication.CustomJWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}
```

### JWT Auth


Generate rsa public/private key

```bash
openssl genrsa -out jwt_template_api_key 1024
openssl rsa -in jwt_template_api_key -pubout -out jwt_template_api_key.pub
```

```python
import environ
from datetime import timedelta
env = environ.Env()

# Simple JWT
EXPIRED_TOKEN_MINUTES = env.int('EXPIRED_TOKEN_MINUTES', default=60)
EXPIRED_REFRESH_DAYS = env.int('EXPIRED_REFRESH_DAYS', default=30)

# JWT PUBLIC/PRIVATE KEY PATH
JWT_PUBLIC_KEY_PATH = env.str('JWT_PUBLIC_KEY_PATH', default='/jwt_template_api_key.pub')
JWT_PRIVATE_KEY_PATH = env.str('JWT_PRIVATE_KEY_PATH', default='/jwt_template_api_key')

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=EXPIRED_TOKEN_MINUTES),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=EXPIRED_REFRESH_DAYS),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,

    'ALGORITHM': 'RS256',
    'SIGNING_KEY': open(JWT_PRIVATE_KEY_PATH).read(),
    'VERIFYING_KEY': open(JWT_PUBLIC_KEY_PATH).read(),

    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'id',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}
```
