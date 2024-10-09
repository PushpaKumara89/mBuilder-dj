import dataclasses

from django.db import models
from safedelete import SOFT_DELETE

from api.models.base_model import BaseModel


@dataclasses.dataclass
class FloorPlanImageSizes:
    width: int
    height: int


class FloorPlanImage(BaseModel):
    _safedelete_policy = SOFT_DELETE

    class Meta(BaseModel.Meta):
        db_table = 'floor_plan_images'

    DPI_SIZES = FloorPlanImageSizes(width=200, height=200)

    plan = models.ForeignKey('Media', on_delete=models.CASCADE)
    image = models.ForeignKey('Media', on_delete=models.CASCADE, related_name='floor_plan_image')
