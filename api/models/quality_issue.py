from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import SET_NULL
from django.utils.translation import gettext_lazy as _
from safedelete import SOFT_DELETE

from api.models.base_model import BaseModel
from api.models.managers.quality_issue import QualityIssueManager
from api.models.queryset.quality_issue_queryset import QualityIssueQuerySet


class QualityIssue(BaseModel):
    _safedelete_policy = SOFT_DELETE

    objects = QualityIssueManager(QualityIssueQuerySet)

    class Meta(BaseModel.Meta):
        db_table = 'quality_issue'

    class Status(models.TextChoices):
        CLOSED = 'closed', _('Closed')
        IN_PROGRESS = 'in_progress', _('In Progress')
        REMOVED = 'removed', _('Removed')
        CONTESTED = 'contested', _('Contested')
        UNDER_INSPECTION = 'under_inspection', _('Under Inspection')
        UNDER_REVIEW = 'under_review', _('Under Review')
        INSPECTION_REJECTED = 'inspection_rejected', _('Inspection Rejected')
        REQUESTING_APPROVAL = 'requesting_approval', _('Requesting Approval')
        REQUESTED_APPROVAL_REJECTED = 'requested_approval_rejected', _('Requested Approval Rejected')
        DECLINED = 'declined', _('Declined')

    location_matrix = models.ForeignKey('LocationMatrix', on_delete=models.CASCADE)
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    status = models.CharField(max_length=255, choices=Status.choices, default=Status.UNDER_REVIEW)
    description = models.TextField()
    attachments = models.ManyToManyField('Media')
    due_date = models.DateTimeField(null=True)
    last_confirmed_update = models.ForeignKey('QualityIssueUpdate', on_delete=models.SET_NULL, null=True)
    old_quality_issue = models.ForeignKey('QualityIssue', on_delete=SET_NULL, default=None, null=True)
    local_id = models.CharField(null=True, blank=True, default=None, max_length=255)
    response_category = models.ForeignKey('ResponseCategory', on_delete=models.SET_NULL, default=None, null=True)
    floor_plan_area_pins = GenericRelation('FloorPlanAreaPin')

    def get_to_report_status_name(self) -> str:
        if self.status == self.Status.DECLINED:
            return _('Subcontractor Declined')
        return dict(self.Status.choices)[self.status]

    @property
    def floor_plan_area_pin(self):
        return self.floor_plan_area_pins.first()

    @property
    def is_under_inspection(self):
        return self.status == self.Status.UNDER_INSPECTION

    @property
    def is_under_review(self):
        return self.status == self.Status.UNDER_REVIEW

    @property
    def is_inspection_rejected(self):
        return self.status == self.Status.INSPECTION_REJECTED.value

    @property
    def is_removed(self):
        return self.status == self.Status.REMOVED.value

    @property
    def is_contested(self):
        return self.status == self.Status.CONTESTED.value

    @property
    def is_in_progress(self):
        return self.status == self.Status.IN_PROGRESS.value

    @property
    def is_requesting_approval(self):
        return self.status == self.Status.REQUESTING_APPROVAL.value

    @property
    def is_requested_approval_rejected(self):
        return self.status == self.Status.REQUESTED_APPROVAL_REJECTED.value

    @property
    def is_closed(self):
        return self.status == self.Status.CLOSED

    @property
    def is_declined(self):
        return self.status == self.Status.DECLINED
