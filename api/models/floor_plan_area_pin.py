from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from safedelete import SOFT_DELETE

from api.models.base_model import BaseModel


class FloorPlanAreaPin(BaseModel):
    _safedelete_policy = SOFT_DELETE

    class Meta(BaseModel.Meta):
        db_table = 'floor_plan_area_pins'

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    floor_plan_area = models.ForeignKey('FloorPlanArea', on_delete=models.CASCADE)
    pin = models.JSONField()
