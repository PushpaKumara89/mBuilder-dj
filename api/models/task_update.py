from api.models.media import Media
from api.models.base_model import BaseModel
from safedelete import SOFT_DELETE
from django.db import models


class TaskUpdate(BaseModel):
    _safedelete_policy = SOFT_DELETE

    class Meta(BaseModel.Meta):
        db_table = 'tasks_updates'

    task = models.ForeignKey('Task', on_delete=models.CASCADE)
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    comment = models.TextField(null=True, blank=True)
    files = models.ManyToManyField(Media)
    old_data = models.JSONField()
    new_data = models.JSONField()
    recipients = models.ManyToManyField('Recipient')
    is_conflict = models.BooleanField(default=False)
    local_id = models.CharField(max_length=255, null=True, default=None)
