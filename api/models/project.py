from django.db import models
from django.db.models import UniqueConstraint, Q
from django.utils.translation import gettext_lazy as _
from djmoney.models.fields import MoneyField
from safedelete import SOFT_DELETE

from api.models.base_model import BaseModel
from api.models.managers import BaseAllManager, BaseManager
from api.models.queryset.project_queryset import ProjectQueryset


class Project(BaseModel):
    _safedelete_policy = SOFT_DELETE

    objects = BaseManager(ProjectQueryset)
    all_objects = BaseAllManager(ProjectQueryset)

    class Meta:
        db_table = 'projects'
        ordering = ['name', 'id']
        constraints = [
            UniqueConstraint(fields=['name'], condition=Q(deleted__isnull=True), name='projects_unique_name_if_not_deleted'),
            UniqueConstraint(fields=['number'], condition=Q(deleted__isnull=True), name='projects_unique_number_if_not_deleted'),
        ]

    class Status(models.TextChoices):
        TENDERING = 'tendering', _('Tendering')
        UNDER_CONSTRUCTION = 'under_construction', _('Under construction')
        PARTIALLY_COMPLETED = 'partially_completed', _('Partially completed')
        COMPLETED = 'completed', _('Completed')
        ARCHIVED = 'archived', _('Archived')

    name = models.CharField(max_length=255)
    number = models.CharField(max_length=255)
    status = models.CharField(max_length=255, choices=Status.choices)
    show_estimated_man_hours = models.BooleanField(default=False)
    image = models.ForeignKey('Media', on_delete=models.CASCADE, null=True)
    start_date = models.DateField()
    completion_date = models.DateField()
    value = MoneyField(max_digits=12, decimal_places=2, default_currency='USD', null=True)
    users = models.ManyToManyField('User', through='ProjectUser')
    key_contacts = models.ManyToManyField('User', related_name='key_contacts')
    is_demo = models.BooleanField(default=False)
    snapshot = models.ForeignKey('Media', on_delete=models.SET_NULL, default=None, null=True, related_name='parent_project')
    is_subtask_visible_for_clients = models.BooleanField(default=False)
    is_task_visible_for_clients = models.BooleanField(default=True)

    @property
    def name_without_spaces(self) -> str:
        return self.name.replace(' ', '-')
