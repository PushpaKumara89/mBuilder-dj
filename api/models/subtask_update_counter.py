from django.db import models

from api.models.base_model import BaseModel
from api.models.managers.subtask_update_counter_manager import SubtaskUpdateCounterManager


class SubtaskUpdateCounter(BaseModel):
    objects = SubtaskUpdateCounterManager()

    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    count = models.IntegerField(default=0)

    class Meta:
        db_table = 'subtask_update_counters'
