from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.db.models import SET_NULL
from django.utils.translation import gettext_lazy as _
from safedelete import SOFT_DELETE

from api.models.base_model import BaseModel
from api.models.fields import DateTimeFieldOmitAutoNowValue
from api.models.managers.subtask import SubtaskManager


class Subtask(BaseModel):
    """
    Model has generated fields `level_number` and `level_postfix`.
    They are created view raw query in migrations because ORM
    doesn't support this kind of fields.
    Also model has two raw indexes `weight_for_staff` and `weight_for_subcontractor`.
    They area include generated fields `level_number` and `level_postfix`.
    """
    _safedelete_policy = SOFT_DELETE

    objects = SubtaskManager()

    class Status(models.TextChoices):
        CLOSED = 'closed', _('Closed')
        IN_PROGRESS = 'in_progress', _('In Progress')
        REMOVED = 'removed', _('Removed')
        CONTESTED = 'contested', _('Contested')
        UNDER_INSPECTION = 'under_inspection', _('Under Inspection')
        INSPECTION_REJECTED = 'inspection_rejected', _('Inspection Rejected')
        REQUESTING_APPROVAL = 'requesting_approval', _('Requesting Approval')
        REQUESTED_APPROVAL_REJECTED = 'requested_approval_rejected', _('Requesting Approval Rejected')
        DECLINED = 'declined', _('Declined')

    class Meta(BaseModel.Meta):
        db_table = 'subtasks'

    task = models.ForeignKey('Task', on_delete=models.CASCADE)
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    description = models.TextField(max_length=255)
    status = models.CharField(max_length=255, choices=Status.choices, default=Status.IN_PROGRESS)
    estimation = models.PositiveIntegerField(null=True, default=None)
    files = models.ManyToManyField('Media')
    due_date = models.DateTimeField()
    quality_issue = models.ForeignKey('QualityIssue', on_delete=SET_NULL, default=None, null=True)
    company = models.ForeignKey('Company', on_delete=SET_NULL, default=None, null=True)
    is_defect = models.BooleanField(default=False)
    last_confirmed_update = models.ForeignKey(
        'SubtaskUpdate',
        on_delete=models.SET_NULL,
        related_name='updated_subtask',
        null=True
    )
    last_update = models.ForeignKey(
        'SubtaskUpdate',
        on_delete=models.SET_NULL,
        related_name='last_subtask_update',
        null=True
    )
    response_due_date = models.DateTimeField(null=True, default=None)
    location_description = models.CharField(null=True, default=None, max_length=50, blank=True)
    building = models.CharField(null=True, max_length=255)
    level = models.CharField(null=True, max_length=255)
    area = models.CharField(null=True, max_length=255)
    project = models.ForeignKey('Project', on_delete=models.CASCADE, null=True)
    local_id = models.CharField(null=True, blank=True, default=None, max_length=255)
    date_of_completion = models.DateTimeField(null=True)
    floor_plan_area_pins = GenericRelation('FloorPlanAreaPin')
    closed_files_count = models.IntegerField(default=0)
    files_count = models.IntegerField(default=0)
    created_at = DateTimeFieldOmitAutoNowValue(auto_now_add=True, null=False, editable=False, blank=False)

    def get_to_report_status_name(self) -> str:
        status = self.status
        if status == self.Status.DECLINED:
            return _('Subcontractor Declined')

        if status == self.Status.INSPECTION_REJECTED:
            status = self.Status.IN_PROGRESS

        return dict(self.Status.choices)[status]

    @property
    def floor_plan_area_pin(self):
        return self.floor_plan_area_pins.first()

    @property
    def is_closed(self):
        return self.status == self.Status.CLOSED

    @property
    def is_in_progress(self):
        return self.status == self.Status.IN_PROGRESS

    @property
    def is_removed(self):
        return self.status == self.Status.REMOVED

    @property
    def is_contested(self):
        return self.status == self.Status.CONTESTED

    @property
    def is_under_inspection(self):
        return self.status == self.Status.UNDER_INSPECTION

    @property
    def is_inspection_rejected(self):
        return self.status == self.Status.INSPECTION_REJECTED

    @property
    def is_requesting_approval(self):
        return self.status == self.Status.REQUESTING_APPROVAL

    @property
    def is_declined(self):
        return self.status == self.Status.DECLINED
