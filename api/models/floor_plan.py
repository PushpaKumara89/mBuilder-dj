import reversion
from django.db import models
from django.db.models import UniqueConstraint, Q
from safedelete import SOFT_DELETE

from api.models.base_model import BaseModel


@reversion.register(follow=('floorplanarea_set',))
class FloorPlan(BaseModel):
    _safedelete_policy = SOFT_DELETE

    class Meta(BaseModel.Meta):
        db_table = 'floor_plans'
        constraints = [
            UniqueConstraint(fields=['project', 'package', 'building', 'level'],
                             name='floor_plans_unique_media', condition=Q(deleted__isnull=True)),
        ]

    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    package = models.ForeignKey('Package', on_delete=models.CASCADE)
    media = models.ForeignKey('Media', on_delete=models.CASCADE)
    building = models.CharField(max_length=255)
    level = models.CharField(max_length=255)

    def get_floor_plan_image(self):
        floor_plan_image = self.media.floorplanimage_set.first()
        if floor_plan_image:
            return floor_plan_image.image
        return None
