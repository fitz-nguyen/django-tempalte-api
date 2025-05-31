from apps.systems import choices
from apps.systems.models import (
    HirePredictionConfig,
    HomeSizeConfig,
    NotInterestedReasonConfig,
    PageConfig,
    RoofMaterialConfig,
    SaleStatusConfig,
    StormDamageConfig,
    SystemConfig,
)
from rest_framework import serializers


class PageConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageConfig
        fields = "__all__"


class PageConfigParamSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=choices.PAGE_CHOICES)


class HomeSizeConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomeSizeConfig
        fields = "__all__"


class HirePredictionConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = HirePredictionConfig
        fields = "__all__"


class SaleStatusConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleStatusConfig
        fields = "__all__"


class StormDamageConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = StormDamageConfig
        fields = "__all__"


class RoofMaterialConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoofMaterialConfig
        fields = "__all__"


class SystemConfigSerializer(serializers.ModelSerializer):
    home_size = serializers.SerializerMethodField()
    storm_damage = serializers.SerializerMethodField()
    hire_prediction = serializers.SerializerMethodField()
    roof_material = serializers.SerializerMethodField()
    sale_status = serializers.SerializerMethodField()
    not_interested_reason = serializers.SerializerMethodField()

    class Meta:
        model = SystemConfig
        fields = "__all__"

    @classmethod
    def get_home_size(cls, obj):
        data = HomeSizeConfigSerializer(HomeSizeConfig.objects.all().order_by("order"), many=True).data
        return data

    @classmethod
    def get_storm_damage(cls, obj):
        data = StormDamageConfigSerializer(StormDamageConfig.objects.all().order_by("order"), many=True).data
        return data

    @classmethod
    def get_hire_prediction(cls, obj):
        return HirePredictionConfigSerializer(HirePredictionConfig.objects.all().order_by("order"), many=True).data

    @classmethod
    def get_sale_status(cls, obj):
        return SaleStatusConfigSerializer(SaleStatusConfig.objects.all().order_by("order"), many=True).data

    @classmethod
    def get_roof_material(cls, obj):
        return RoofMaterialConfigSerializer(RoofMaterialConfig.objects.all().order_by("order"), many=True).data

    @classmethod
    def get_not_interested_reason(cls, obj):
        return NotInterestedReasonConfig.objects.all().values_list("value", flat=True)
