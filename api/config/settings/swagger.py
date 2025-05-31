import os

from django.urls import reverse_lazy

# Swagger Setting
# https://drf-yasg.readthedocs.io/en/stable/settings.html

OAUTH2_CLIENT_ID = os.environ.get("OAUTH2_CLIENT_ID", default="")
OAUTH2_CLIENT_SECRET = os.environ.get("OAUTH2_CLIENT_SECRET", default="")
OAUTH2_APP_NAME = os.environ.get("OAUTH2_APP_NAME", default="Template API")

SWAGGER_SETTINGS = {
    "USE_SESSION_AUTH": False,
    "LOGIN_URL": reverse_lazy("admin:login"),
    "LOGOUT_URL": reverse_lazy("admin:logout"),
    "VALIDATOR_URL": None,
    "REFETCH_SCHEMA_WITH_AUTH": True,
    "REFETCH_SCHEMA_ON_LOGOUT": True,
    "SECURITY_DEFINITIONS": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Authorize with token, Format: Bearer <token> or token <token>",
        },
        "oauth2": {
            "type": "oauth2",
            "flow": "password",
            "tokenUrl": "/v1/o/token/",
            "description": "A short description for oauth2 security scheme.",
        },
    },
    "OAUTH2_CONFIG": {
        "clientId": OAUTH2_CLIENT_ID,
        "clientSecret": OAUTH2_CLIENT_SECRET,
        "appName": OAUTH2_APP_NAME,
    },
}
