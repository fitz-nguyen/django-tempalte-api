App Notification
---
Django App for sending Notification.

## Prerequisites
- package `fcm_django`

## Setup
Edit your `settings/common.py` file:

```python
THIRD_PARTY_APPS = (
    # ...
    'fcm_django'
    # ...
)

LOCAL_APPS = (
    # ...
    'apps.notification'
    # ...
)

# https://github.com/xtrinch/fcm-django
FCM_DJANGO_SETTINGS = {
    "APP_VERBOSE_NAME": "[string for AppConfig's verbose_name]",
     # default: _('FCM Django')
    "FCM_SERVER_KEY": "[your api key]",
     # true if you want to have only one active device per registered user at a time
     # default: False
    "ONE_DEVICE_PER_USER": True/False,
     # devices to which notifications cannot be sent,
     # are deleted upon receiving error response from FCM
     # default: False
    "DELETE_INACTIVE_DEVICES": True/False,
}

# You can customize Push Service
APP_NOTIFICATION = {
    'DEFAULT_PUSHER_CLASS': 'apps.notification.pushers.FireBasePusher'
}
```


## Endpoints
These endpoint requires an Authenticated User.

### Register FCM devices
```bash
POST /v1/notifications/fcm/devices/
```

### List notifications
```bash
GET /v1/notifications/
```

### Mark as read
```bash
POST /v1/notifications/read/
```

### Mask as archived
```bash
POST /v1/notifications/archive/
```

### Get badge
```bash
GET /v1/notifications/badge/
```

## Usage
```python
from apps.notification.services.message import NotificationMessage
from apps.notification.services.manager import NotificationManager

class MyMessage(NotificationMessage):

    def __init__(self, _user):
        self._user = _user

    @property
    def user(self):
        return self._user

    @property
    def verb(self) -> str:
        return 'my verb'

    @property
    def content(self):
        return 'my content'

    @property
    def template(self):
        return 'my template'

user = None #
NotificationManager.send(MyMessage(user=user))
```
