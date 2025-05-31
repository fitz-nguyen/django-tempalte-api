import environ

env = environ.Env()
env.read_env()

# AWS S3
USE_S3 = env.bool("USE_S3", default=False)
if USE_S3:
    AWS_ACCESS_KEY_ID = env("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = env("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_CUSTOM_DOMAIN = env("AWS_S3_CUSTOM_DOMAIN", default=f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com")
    AWS_S3_OBJECT_PARAMETERS = {
        "CacheControl": "max-age=86400",
    }
    # The number of seconds that a generated URL is valid for.
    S3_PRE_SIGNED_POST_URL_EXPIRES = env.int("S3_PRE_SIGNED_POST_URL_EXPIRES", default=300)
    AWS_LOCATION = env("AWS_LOCATION", default="media")  # A path prefix that will be prepended to all uploads.
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
