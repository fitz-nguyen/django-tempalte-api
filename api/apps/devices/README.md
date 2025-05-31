App Devices
---

## Overview
This application support to keep track these device with user.

## Prerequisites
- package `logging`



### Installed apps
```python
LOCAL_APPS = (
    # ...
       "apps.devices.apps.DevicesConfig",
    # ...
)

```
### Middleware
```python
MIDDLEWARE = [
    # ...
     "apps.devices.middleware.DeviceIDLoggerMiddleware",
]
```
