from django.db import models
from django.db.models import UniqueConstraint
from django.utils.translation import gettext_lazy as _
from safedelete import SOFT_DELETE

from api.models.base_model import BaseModel
from api.models.managers import BaseManager, BaseAllManager, BaseDeletedManager
from api.models.queryset.package_handover_document_media_queryset import PackageHandoverDocumentMediaQueryset


class PackageHandoverDocumentMedia(BaseModel):
    _safedelete_policy = SOFT_DELETE

    objects = BaseManager(PackageHandoverDocumentMediaQueryset)
    all_objects = BaseAllManager(PackageHandoverDocumentMediaQueryset)
    deleted_objects = BaseDeletedManager(PackageHandoverDocumentMediaQueryset)

    class Status(models.TextChoices):
        IN_PROGRESS = 'in_progress', _('In progress')
        CONTESTED = 'contested', _('Contested')
        REQUESTING_APPROVAL = 'requesting_approval', _('Requesting approval')
        REQUESTED_APPROVAL_REJECTED = 'requested_approval_rejected', _('Requested approval rejected')
        ACCEPTED = 'accepted', _('Accepted')
        REMOVED = 'removed', _('Removed')

    class Meta(BaseModel.Meta):
        db_table = 'package_handover_document_media'
        constraints = [
            UniqueConstraint(fields=['uid'],
                             name='package_handover_document_media_unique_uid',
                             condition=models.Q(deleted__isnull=True))
        ]

    package_handover_document = models.ForeignKey('PackageHandoverDocument', on_delete=models.CASCADE)
    media = models.ForeignKey('Media', on_delete=models.CASCADE)
    status = models.CharField(max_length=255, choices=Status.choices, default=Status.IN_PROGRESS.value)
    uid = models.CharField(max_length=255, null=True, default=None)
    information = models.TextField(null=True, blank=True)
    last_confirmed_update = models.ForeignKey('PackageHandoverDocumentMediaUpdate', on_delete=models.SET_NULL, null=True)

    @property
    def is_requesting_approval(self):
        return self.status == self.Status.REQUESTING_APPROVAL

    @property
    def is_requesting_approval_rejected(self):
        return self.status == self.Status.REQUESTED_APPROVAL_REJECTED

    @property
    def is_in_progress(self):
        return self.status == self.Status.IN_PROGRESS

    @property
    def is_contested(self):
        return self.status == self.Status.CONTESTED

    @property
    def is_accepted(self):
        return self.status == self.Status.ACCEPTED

    @property
    def is_removed(self):
        return self.status == self.Status.REMOVED
