from api.models.managers import BaseManager
from api.models.media import Media
from api.models.base_model import BaseModel
from safedelete import SOFT_DELETE
from django.db import models

from api.models.queryset.subtask_update_queryset import SubtaskUpdateQueryset


class SubtaskUpdate(BaseModel):
    _safedelete_policy = SOFT_DELETE

    objects = BaseManager(SubtaskUpdateQueryset)

    class Meta(BaseModel.Meta):
        db_table = 'subtasks_updates'

    subtask = models.ForeignKey('Subtask', on_delete=models.CASCADE)
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    comment = models.TextField(null=True, blank=True)
    files = models.ManyToManyField(Media)
    old_data = models.JSONField()
    new_data = models.JSONField()
    recipients = models.ManyToManyField('Recipient')
    is_conflict = models.BooleanField(default=False)
    local_id = models.CharField(max_length=255, null=True, default=None)
    is_comment = models.BooleanField(default=False)
