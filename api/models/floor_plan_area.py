import reversion
from django.db import models
from django.db.models import UniqueConstraint
from safedelete import SOFT_DELETE

from api.models.base_model import BaseModel


@reversion.register(follow=('floor_plan',))
class FloorPlanArea(BaseModel):
    _safedelete_policy = SOFT_DELETE

    class Meta(BaseModel.Meta):
        db_table = 'floor_plan_areas'
        constraints = [
            UniqueConstraint(
                fields=['floor_plan', 'area'],
                name='floor_plan_areas_uniqueness',
                condition=models.Q(deleted__isnull=True)
            )
        ]

    floor_plan = models.ForeignKey('FloorPlan', on_delete=models.CASCADE)
    polygon = models.JSONField()
    area = models.CharField(max_length=255)
