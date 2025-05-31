from apps.systems.models import (
    HirePredictionConfig,
    HomeSizeConfig,
    NotInterestedReasonConfig,
    RoofMaterialConfig,
    SaleStatusConfig,
    StormDamageConfig,
    SystemConfig,
)
from apps.systems.utils import SystemConfigCache
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=StormDamageConfig)
@receiver(post_save, sender=SystemConfig)
@receiver(post_save, sender=HomeSizeConfig)
@receiver(post_save, sender=RoofMaterialConfig)
@receiver(post_save, sender=HirePredictionConfig)
@receiver(post_save, sender=SaleStatusConfig)
@receiver(post_save, sender=NotInterestedReasonConfig)
def clear_cache_system(sender, created: bool, instance, **kwargs):
    SystemConfigCache().delete_cache()
