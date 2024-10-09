from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from safedelete import SOFT_DELETE

from api.models.base_model import BaseModel


class HandoverDocumentArchive(BaseModel):
    _safedelete_policy = SOFT_DELETE

    class Status(models.TextChoices):
        IN_PROGRESS = 'in_progress', _('In progress')
        COMPLETED = 'completed', _('Completed')

    class Meta(BaseModel.Meta):
        db_table = 'handover_document_archives'
        constraints = (
            models.UniqueConstraint(
                fields=('project', 'user'),
                name='handover_document_archives_uniqueness',
                condition=~Q(status='completed')
            ),
        )

    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    status = models.CharField(max_length=11, choices=Status.choices, default=Status.IN_PROGRESS)
    generation_started_at = models.DateTimeField()
