import json
import uuid
from datetime import date, datetime

from apps.systems.models import (
    HirePredictionConfig,
    HomeSizeConfig,
    RoofMaterialConfig,
    SaleStatusConfig,
    StormDamageConfig,
    SystemConfig,
)
from dateutil.parser import parse  # type:ignore
from django.conf import settings

from apps.core.redis import get_redis
from apps.core.utils import cache_model_instance, get_cache_model_instance


class SystemConfigCache:
    def __init__(self):
        self.client = get_redis(db=0)
        self.key = "SYSTEM_CONFIG_CACHE"
        self.ttl = settings.TTL_SYSTEM_CONFIG_CACHE

    def _dict_handle(self, v):
        if isinstance(v, datetime):
            return f"DATETIME+{v.isoformat()}"
        elif isinstance(v, date):
            return f"DATE+{v.isoformat()}"
        elif isinstance(v, uuid.UUID):
            return str(v)

    def set(self):
        system_config = SystemConfig.objects.first()
        data = {
            "storm_damage": {
                item["value"]: {"unit_value": item["unit_value"], "unit": item["unit"]}
                for item in StormDamageConfig.objects.all().values("value", "unit_value", "unit").iterator()
            },
            "home_size": {
                item["value"]: {"total_sqft_from": item["total_sqft_from"], "total_sqft_to": item["total_sqft_to"]}
                for item in HomeSizeConfig.objects.all().values("value", "total_sqft_from", "total_sqft_to").iterator()
            },
            "sale_status": list(SaleStatusConfig.objects.all().values_list("value", flat=True)),
            "hire_prediction": {
                item["value"]: {"key": item["key"], "hex_color": item["hex_color"], "icon_url": item["icon_url"]}
                for item in HirePredictionConfig.objects.all()
                .values("key", "value", "hex_color", "icon_url")
                .iterator()
            },
            "reach_valid_distance": system_config.reach_valid_distance,
            "customer_lead_import_limit": system_config.customer_lead_import_limit,
            "csv_map_generation_duration": system_config.csv_map_generation_duration,
            "customer_max_lead_file_size": system_config.customer_max_lead_file_size,
            "email_footer_url": system_config.email_footer_url,
            "roof_material": list(RoofMaterialConfig.objects.all().values_list("value", flat=True)),
        }
        json_str = json.dumps(data, default=self._dict_handle)
        self.client.set(self.key, json_str, ex=self.ttl)
        return data

    def _dict_parse(self, dict_data):
        for k, v in dict_data.items():
            if k == "id":
                dict_data[k] = uuid.UUID(v)
            elif str(v).startswith("DATE+"):
                dict_data[k] = parse(v.split("DATE+")[1]).date()
            elif str(v).startswith("DATETIME+"):
                dict_data[k] = parse(v.split("DATETIME+")[1])
            else:
                continue
        return dict_data

    def get(self):
        json_str = self.client.get(self.key)
        if not json_str:
            return self.set()
        return json.loads(json_str)

    @property
    def storm_damage_config(self):
        return self.get()["storm_damage"]

    @property
    def home_size_config(self):
        return self.get()["home_size"]

    @property
    def reach_valid_distance(self):
        return self.get()["reach_valid_distance"]

    @property
    def csv_map_generation_duration(self):
        return self.get()["csv_map_generation_duration"]

    @property
    def customer_lead_import_limit(self):
        return self.get()["customer_lead_import_limit"]

    @property
    def email_footer_url(self):
        return self.get()["email_footer_url"]

    @property
    def customer_max_lead_file_size(self):
        return self.get()["customer_max_lead_file_size"]

    @property
    def roof_material(self):
        return self.get()["roof_material"] if self.get()["roof_material"] else []

    @property
    def sale_status(self):
        return self.get()["sale_status"] if self.get()["sale_status"] else []

    @property
    def hire_prediction_config(self):
        return self.get()["hire_prediction"] if self.get()["hire_prediction"] else {}

    def delete_cache(self):
        self.client.delete(self.key)


def get_system_config():
    cache_key = "system_config_cache"
    system_config = get_cache_model_instance(cache_key)
    if not system_config:
        system_config = SystemConfig.objects.first()
        cache_model_instance(cache_key=cache_key, instance=system_config)

    return system_config
