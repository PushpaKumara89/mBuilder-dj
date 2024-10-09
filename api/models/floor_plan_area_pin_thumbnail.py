from django.db import models
from django.db.models import TextChoices
from safedelete import SOFT_DELETE

from api.models.base_model import BaseModel


class FloorPlanAreaPinThumbnail(BaseModel):
    _safedelete_policy = SOFT_DELETE

    class Type(TextChoices):
        GENERAL = 'general'
        AREA = 'area'

    class Meta(BaseModel.Meta):
        db_table = 'floor_plan_area_pin_thumbnails'

    floor_plan_area_pin = models.ForeignKey('FloorPlanAreaPin', on_delete=models.CASCADE)
    thumbnail = models.ForeignKey('Media', on_delete=models.CASCADE)
    type = models.CharField(choices=Type.choices, max_length=255, null=True)
