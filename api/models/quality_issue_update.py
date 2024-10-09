from api.models.managers.quality_issue_update_base_manager import QualityIssueUpdateBaseManager
from api.models.media import Media
from api.models.base_model import BaseModel
from safedelete import SOFT_DELETE
from django.db import models

from api.models.queryset.quality_issue_update_queryset import QualityIssueUpdateQueryset


class QualityIssueUpdate(BaseModel):
    _safedelete_policy = SOFT_DELETE

    objects = QualityIssueUpdateBaseManager(QualityIssueUpdateQueryset)

    class Meta(BaseModel.Meta):
        db_table = 'quality_issue_updates'

    quality_issue = models.ForeignKey('QualityIssue', on_delete=models.CASCADE)
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    comment = models.TextField(null=True, blank=True)
    files = models.ManyToManyField(Media)
    old_data = models.JSONField()
    new_data = models.JSONField()
    recipients = models.ManyToManyField('Recipient')
    is_conflict = models.BooleanField(default=False)
    local_id = models.CharField(max_length=255, null=True, default=None)
    is_comment = models.BooleanField(default=False)
