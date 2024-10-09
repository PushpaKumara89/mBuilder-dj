from django.db import models
from reversion.models import Revision
from safedelete import SOFT_DELETE

from api.enums import ChoiceEnum
from api.models.base_model import BaseModel


class FloorPlanRevisionMeta(BaseModel):
    _safedelete_policy = SOFT_DELETE

    class EventTypes(ChoiceEnum):
        FILE_UPDATED = 'file_updated'
        FILE_UPLOADED = 'file_uploaded'
        AREAS_UPDATED = 'areas_updated'

    class Meta(BaseModel.Meta):
        db_table = 'floor_plan_revision_meta'

    revision = models.ForeignKey(Revision, on_delete=models.CASCADE)
    event_type = models.CharField(max_length=255)
