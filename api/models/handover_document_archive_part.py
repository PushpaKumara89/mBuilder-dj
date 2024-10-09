from django.db import models
from django.utils.translation import gettext_lazy as _
from safedelete import SOFT_DELETE

from api.models.base_model import BaseModel


class HandoverDocumentArchivePart(BaseModel):
    _safedelete_policy = SOFT_DELETE

    class Status(models.TextChoices):
        WAITING = 'waiting', _('Waiting')
        RUNNING = 'running', _('Running')
        FAILED = 'failed', _('Failed')
        SAVED = 'saved', _('Saved')
        SENT = 'sent', _('Sent')

    class Meta(BaseModel.Meta):
        db_table = 'handover_document_archive_parts'

    handover_document_archive = models.ForeignKey('HandoverDocumentArchive', on_delete=models.CASCADE)
    asset_handover_media_range = models.JSONField(default=dict)
    package_handover_media_range = models.JSONField(default=dict)
    in_range_files_count = models.IntegerField(default=0)
    total_files_count = models.IntegerField(default=0)
    media = models.ForeignKey('Media', null=True, on_delete=models.SET_NULL)
    status = models.CharField(max_length=7, choices=Status.choices, default=Status.WAITING)
    error_track_id = models.CharField(max_length=255, null=True)

    @property
    def is_failed(self):
        return self.status == self.Status.FAILED
