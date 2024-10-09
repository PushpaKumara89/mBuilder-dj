from django.db import models
from safedelete import HARD_DELETE

from api.models.base_model import BaseModel


class EditMode(BaseModel):
    create_events_on_update = False

    _safedelete_policy = HARD_DELETE

    class Meta(BaseModel.Meta):
        db_table = 'edit_mode'

    project = models.ForeignKey('Project', on_delete=models.CASCADE, null=True)
    entity = models.CharField(max_length=255)
    entity_id = models.IntegerField(null=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE)
