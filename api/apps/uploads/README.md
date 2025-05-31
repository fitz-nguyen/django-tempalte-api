App Uploads
---
Django App for Upload File .

## Overview

This application is an implementation of API can upload file to File Storage

## Prerequisites
- package `python_magic`

- On Mac: we need to install libmagic  `brew install libmagic`

## Setup
Edit your `settings/common.py` file:

```python
LOCAL_APPS = (
    # ...
    'apps.uploads'
    # ...
)
```
## Endpoints
These endpoint does not requires an Authenticated User.

### Uploads file
```bash
POST /v1/uploads/
```
In body of request, you need to add attribute "folder_name" which folder save your files
```bash
#....
"folder_name": "folder"
#....
```

###Usage
## Mark file used
In body of request, you need to add attribute "folder_name" which folder save your files
```bash
#....
"folder_name": "folder"
#....
```

###Usage
## Mark file used
In body of request, you need to add attribute "folder_name" which folder save your files
```bash
#....
"folder_name": "folder"
#....
```

###Usage
## Mark file used
```python
from apps.uploads.services.usercases import UploadFileService
file_path = ""
file_id = None
UploadFileService().mark_file_used(file_path, file_id)
```

## Mark file delete
```python
from apps.uploads.services.usercases import UploadFileService
file_path = ""
UploadFileService().delete(file_path)
```

## Create image thumbnail
```python
from apps.uploads.services.usercases import UploadFileService
file_path = ""
thumb_size = (300, 300)
UploadFileService().create_thumbnail(file_path, thumb_size)

```

## Generate Pre Signed URL for S3 Endpoint
```bash
GET /v1/uploads/s3/pre-signed-post-url/
```
####You need to pass these params:
```bash
file_name: ....
file_type: ....
folder_name: ...
```

