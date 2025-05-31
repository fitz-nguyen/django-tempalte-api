# type: ignore
import colorsys
import logging
import random
import re
import string
import time
from datetime import datetime
from logging import Logger
from os import path
from random import randint
from typing import Optional

import boto3
import pytz
from django.conf import settings
from django.core import serializers
from django.core.cache import cache as core_cache
from django.core.files.storage import default_storage
from django.db.models import CharField, Func, Q, Value
from django.db.models.functions import Collate
from ipware import get_client_ip

logger = logging.getLogger(__name__)


def get_logger(name: Optional[str] = "django") -> Logger:
    return logging.getLogger(name)


def get_now() -> datetime:
    return datetime.now(tz=pytz.utc)


def get_utc_now() -> datetime:
    """
    Get current UTC time
    :return:
    """
    return get_now().replace(tzinfo=pytz.utc)


def generate_password(password_length=20) -> str:
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz23456789!@#$"
    return "".join(random.choice(chars) for i in range(password_length))


def generate_candidate_code(lenght_code=10) -> str:
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ0123456789"
    return "".join(random.choice(chars) for i in range(lenght_code))


def is_number(s: Optional[str]) -> bool:
    try:
        if s is None:
            return False
        float(str(s))  # for int, long and float
    except ValueError:
        return False
    return True


def is_production() -> bool:
    return settings.ENVIRONMENT == "production"


def get_app_version(request) -> Optional[str]:
    if not request or not hasattr(request, "META") or not isinstance(request.META, dict):
        return None
    return request.META.get("HTTP_APP_VERSION")


def get_device_id(request) -> Optional[str]:
    if not request or not hasattr(request, "META") or not isinstance(request.META, dict):
        return None
    return request.META.get("HTTP_DEVICE_ID")


def get_platform(request):
    try:
        if request.user_agent.os.family == "iOS":
            return "IOS"
        if request.user_agent.os.family == "Android":
            return "DROID"

        return "OTHER"
    except Exception as e:
        logger.warning(e)

    return None


def get_platform_version(request):
    try:
        return request.user_agent.os.version_string
    except Exception as e:
        logger.warning(e)

    return None


def get_ip_address(request) -> str:
    client_ip, _ = get_client_ip(request)
    return client_ip


def is_absolute_url(url: str) -> bool:
    if re.match(r"^https?://", url):
        return True
    return False


def get_static_url(file_path: str) -> str:
    if is_absolute_url(file_path):
        return file_path
    url = f"{settings.STATIC_URL}{file_path}"
    return get_absolute_url(url)


def get_media_url(file_path: str) -> str:
    if is_absolute_url(file_path):
        return file_path
    url = default_storage.url(file_path.lstrip("/"))
    return get_absolute_url(url)


def get_absolute_url(url: str) -> str:
    if is_absolute_url(url):
        return url

    base_url = str(settings.BASE_URL).rstrip("/")
    return f'{base_url}/{url.lstrip("/")}'


def get_storage_path(filename: str, folder_name: str) -> str:
    now = datetime.now()
    folder = "/".join(["media", folder_name, str(now.year), f"{now:%m}", f"{now:%d}"])
    path_url = [folder, path.basename(filename)]
    return "/".join(path_url)


def get_datetime_now_to_string(str_format="%m_%d_%Y-%I_%M_%S_%p"):
    return datetime.now().strftime(str_format)


def generate_pre_signed_url_for_s3(file_name: str, file_type: str):
    bucket_name = settings.AWS_LOCATION
    s3 = boto3.client("s3")
    pre_signed_post = s3.generate_presigned_post(
        Bucket=bucket_name,
        Key=file_name,
        Fields={"acl": "public-read", "Content-Type": file_type},
        Conditions=[{"acl": "public-read"}, {"Content-Type": file_type}],
        ExpiresIn=settings.S3_PRE_SIGNED_POST_URL_EXPIRES,
    )
    return pre_signed_post


def random_with_n_digits(n, is_testing=None):
    if is_testing:
        return settings.TESTING_RESET_PASSWORD_OTP
    range_start = 10 ** (n - 1)
    range_end = (10**n) - 1
    return randint(range_start, range_end)


def is_reset_password_otp_expired(created_time) -> bool:
    return (int(time.time()) - created_time.timestamp()) > settings.RESET_PASSWORD_OTP_EXPIRE_TIME


def random_string():
    chars_fixed = string.ascii_letters + string.digits
    min_size_pass = 8
    max_size_pass = 16
    username = "".join(random.choice(chars_fixed) for x in range(random.randint(min_size_pass, max_size_pass)))
    return username


def fake_email(prefix: str = None) -> str:
    if not prefix:
        prefix = random_string().lower()
    return prefix + settings.FAKE_EMAIL_FORMAT


def check_fake_email(email: str) -> bool:
    return True if settings.FAKE_EMAIL_FORMAT in email else False


def add_foreign_keys_to_copy(dict_objects, object_copied):
    try:
        dict_objects[object_copied.__class__].append(object_copied)
    except KeyError:
        dict_objects[object_copied.__class__] = [object_copied]


def bulk_create_with_foreign_keys(foreign_keys):
    for cls, list_of_fks in foreign_keys.items():
        cls.objects.bulk_create(list_of_fks)


def generate_campaign_id(password_length=10) -> str:
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ123456789"
    return "".join(random.choice(chars) for i in range(password_length))


def sort_digit(item):
    if item.isdigit():
        return int(item)
    return 9223372036854775807


def hex_to_hsl(hex_code):
    """Converts a hexadecimal color code to HSL values.

    Args:
      hex_code: A hexadecimal color code.

    Returns:
      A tuple of three floats representing the hue, saturation, and lightness of the color.
    """
    hex_code = hex_code.lstrip("#")
    rgb = tuple(int(hex_code[i : i + 2], 16) for i in (0, 2, 4))
    return colorsys.rgb_to_hls(*rgb)


def array_string_compare(origin_str: str, new_str: str):
    """
    Check if any item is remove or add from string array new_str to array origin_str.
        Args:
          origin_str: A string array
          new_str: A string array

        Returns:
          A tuple with add and remove item
    """
    origin_str = origin_str.split(";") if origin_str else []
    new_str = new_str.split(";") if new_str else []
    # Finding the tags that were added
    added_tags = [item for item in new_str if item not in origin_str and item]
    # Finding the tags that were removed
    removed_tags = [item for item in origin_str if item not in new_str and item]
    return added_tags, removed_tags


def get_aws_lambda_export_csv_hook():
    return settings.INTERNAL_BASE_URL + "/v1/dashboard/lambda-hook/"


def get_filename_path_for_csv_file(folder_name: str) -> str:
    return f"media/dashboard/{folder_name}/dashboard_data_{get_datetime_now_to_string()}"


def format_collate_condition(field, value):
    operators = {
        "__iexact": lambda f, v: Q(**{f: Collate(Value(v, output_field=CharField()), "case_insensitive")}),
        "__iin": lambda f, v: Q(
            **{f + "__in": [Collate(Value(val, output_field=CharField()), "case_insensitive") for val in v]}
        ),
        "__icontains": lambda f, v: Q(**{f + "__icontains": v}),
        "__istartswith": lambda f, v: Q(
            **{
                f + "__gte": Collate(Value(v, output_field=CharField()), "case_insensitive"),
                f + "__lt": Collate(Value(v + chr(255), output_field=CharField()), "case_insensitive"),
            }
        ),
        "__in": lambda f, v: Q(**{f + "__in": v}),
        "__exact": lambda f, v: Q(**{f: v}),
        # "__gte": lambda f, v: Q(**{f + "__gte": v}),
        # "__lte": lambda f, v: Q(**{f + "__lte": v}),
        "__startswith": lambda f, v: Q(**{f + "__startswith": v}),
    }

    for op, formatter in operators.items():
        if field.endswith(op):
            return formatter(field.replace(op, ""), value)

    return Q(**{field: value})


def convert_conditions(query):
    def convert_node(node):
        if isinstance(node, Q):
            new_children = []
            for child in node.children:
                if isinstance(child, Q):
                    new_children.append(convert_node(child))
                else:
                    new_children.append(format_collate_condition(child[0], child[1]))
            return Q(*new_children, _connector=node.connector, _negated=node.negated)
        elif isinstance(node, (list, tuple)):
            if node[0] in ("AND", "OR"):
                connector = node[0]
                conditions = [convert_node(child) for child in node[1:]]
                return Q(*conditions, _connector=connector)
            else:
                return format_collate_condition(node[0], node[1])
        elif isinstance(node, dict):
            connector = node.get("connector", "AND")
            children = node.get("children", [])
            conditions = [convert_node(child) for child in children]
            return Q(*conditions, _connector=connector)
        elif isinstance(node, str) and node in ("AND", "OR"):
            return Q()
        else:
            raise ValueError(f"Unsupported query type: {type(node)}")

    return convert_node(query)


def cache_model_instance(cache_key, instance, expires=60 * 5):
    if not instance:
        return
    serialized_instance = serializers.serialize("json", [instance])
    core_cache.set(cache_key, serialized_instance, timeout=expires)


def get_cache_model_instance(cache_key):
    cached_data = core_cache.get(cache_key)
    try:
        for instance in serializers.deserialize("json", cached_data):
            return instance.object
    except Exception:
        return None


def to_pascal_case(text):
    """Convert string to PascalCase."""
    return ''.join(word.capitalize() for word in text.replace('_', ' ').split())
