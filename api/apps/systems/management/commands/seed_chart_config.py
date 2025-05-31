from apps.systems.models import (
    HirePredictionConfig,
    HomeSizeConfig,
    NotInterestedReasonConfig,
    RoofMaterialConfig,
    SaleStatusConfig,
    StormDamageConfig,
)
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        for model in [
            HirePredictionConfig,
            HomeSizeConfig,
            RoofMaterialConfig,
            SaleStatusConfig,
            NotInterestedReasonConfig,
            StormDamageConfig,
        ]:
            model.objects.all().delete()

        hire_prediction_data = [
            {"id": 3, "value": "Unlikely", "key": "Unlikely", "order": 3},
            {"id": 1, "value": "Likely", "key": "Likely", "order": 1},
            {"id": 2, "value": "Possible", "key": "Possible", "order": 2},
        ]

        home_size_config_data = [
            {
                "id": 3,
                "key": "Standard",
                "total_sqft_from": 2000,
                "total_sqft_to": 2600,
                "description": "2,000 to 2,600 sq ft",
                "order": 3,
                "value": "Standard",
            },
            {
                "id": 5,
                "key": "Luxury",
                "total_sqft_from": 4000,
                "total_sqft_to": None,
                "description": "Larger than 4000sq ft",
                "order": 5,
                "value": "Luxury",
            },
            {
                "id": 1,
                "key": "Small",
                "total_sqft_from": 0,
                "total_sqft_to": 1200,
                "description": "0 to 1,200 sq ft",
                "order": 1,
                "value": "Small",
            },
            {
                "id": 2,
                "key": "Mid-Size",
                "total_sqft_from": 1200,
                "total_sqft_to": 2000,
                "description": "1,200 to 2,000 sq ft",
                "order": 2,
                "value": "Mid-Size",
            },
            {
                "id": 4,
                "key": "Large",
                "total_sqft_from": 2600,
                "total_sqft_to": 4000,
                "description": "2,600 to 4,000 sq ft",
                "order": 4,
                "value": "Large",
            },
        ]
        roof_material = [
            {"id": 2, "value": "Metal", "key": "Metal", "order": 2},
            {"id": 4, "value": "Unknown", "key": "Unknown", "order": 4},
            {"id": 3, "value": "Title", "key": "Title", "order": 3},
            {"id": 1, "value": "Composition Shingle", "key": "Composition Shingle", "order": 1},
        ]

        sale_status = [
            {"id": 5, "value": "Not Interested", "hex_color": "#CECECE", "key": "Not Interested", "order": 5},
            {"id": 2, "value": "Interested", "hex_color": "#D56BBE", "key": "Interested", "order": 2},
            {"id": 1, "value": "New", "hex_color": "#2058BC", "key": "New", "order": 1},
            {"id": 4, "value": "Signed Up", "hex_color": "#C49C2C", "key": "Signed Up", "order": 4},
            {
                "id": 3,
                "value": "Inspection Scheduled",
                "hex_color": "#2CC4A6",
                "key": "Inspection Scheduled",
                "order": 3,
            },
        ]

        storm_damage_data = [
            {
                "id": 5,
                "key": "Within Last 12 Months",
                "value": "Within Last 12 Months",
                "unit": "months",
                "order": 2,
                "unit_value": 12,
            },
            {
                "id": 2,
                "key": "Within Last 3 Months",
                "value": "Within Last 3 Months",
                "unit": "months",
                "order": 4,
                "unit_value": 3,
            },
            {
                "id": 4,
                "key": "Within Last 2 Years",
                "value": "Within Last 2 Years",
                "unit": "years",
                "order": 1,
                "unit_value": 2,
            },
            {
                "id": 3,
                "key": "Within Last 6 Months",
                "value": "Within Last 6 Months",
                "unit": "months",
                "order": 3,
                "unit_value": 6,
            },
            {
                "id": 1,
                "key": "Within Last Week",
                "value": "Within Last Week",
                "unit": "weeks",
                "order": 5,
                "unit_value": 1,
            },
        ]
        reason = [
            "New Roof",
            "Doesn’t think there’s damage",
            "Can’t afford it",
            "Going with another company",
            "Unspecified",
        ]
        hire_prediction_create = []
        for item in hire_prediction_data:
            hire_prediction_create.append(
                HirePredictionConfig(key=item.get("key"), value=item.get("value"), order=item.get("order"))
            )
        HirePredictionConfig.objects.bulk_create(hire_prediction_create)

        home_size_config_create = []
        for item in home_size_config_data:
            home_size_config_create.append(
                HomeSizeConfig(
                    key=item.get("key"),
                    value=item.get("value"),
                    order=item.get("order"),
                    total_sqft_from=item.get("total_sqft_from"),
                    total_sqft_to=item.get("total_sqft_to"),
                    description=item.get("description"),
                )
            )
        HomeSizeConfig.objects.bulk_create(home_size_config_create)

        roof_material_create = []
        for item in roof_material:
            roof_material_create.append(
                RoofMaterialConfig(key=item.get("key"), value=item.get("value"), order=item.get("order"))
            )
        RoofMaterialConfig.objects.bulk_create(roof_material_create)
        sale_status_create = []
        for item in sale_status:
            sale_status_create.append(
                SaleStatusConfig(
                    key=item.get("key"),
                    value=item.get("value"),
                    order=item.get("order"),
                    hex_color=item.get("hex_color"),
                )
            )
        SaleStatusConfig.objects.bulk_create(sale_status_create)

        storm_damage_create = []
        for item in storm_damage_data:
            storm_damage_create.append(
                StormDamageConfig(
                    key=item.get("key"),
                    value=item.get("value"),
                    order=item.get("order"),
                    unit_value=item.get("unit_value"),
                    unit=item.get("unit"),
                )
            )
        StormDamageConfig.objects.bulk_create(storm_damage_create)

        reason_create = []
        for item in reason:
            reason_create.append(NotInterestedReasonConfig(value=item))
        NotInterestedReasonConfig.objects.bulk_create(reason_create)
