from safedelete import HARD_DELETE
from django.db import models

from api.models.base_model import BaseModel


class ProjectUser(BaseModel):
    _safedelete_policy = HARD_DELETE

    class Meta(BaseModel.Meta):
        db_table = 'project_users'
        constraints = [
            models.UniqueConstraint(
                fields=('project', 'user',),
                name='project_user_unique'
            )
        ]

    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    is_notifications_enabled = models.BooleanField(default=False)
