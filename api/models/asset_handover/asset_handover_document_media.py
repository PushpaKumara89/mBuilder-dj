from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from safedelete import SOFT_DELETE

from api.models.base_model import BaseModel
from api.models.managers import BaseManager, BaseAllManager, BaseDeletedManager
from api.models.queryset.asset_handover_document_media_queryset import AssetHandoverDocumentMediaQueryset


class AssetHandoverDocumentMedia(BaseModel):
    _safedelete_policy = SOFT_DELETE

    objects = BaseManager(AssetHandoverDocumentMediaQueryset)
    all_objects = BaseAllManager(AssetHandoverDocumentMediaQueryset)
    deleted_objects = BaseDeletedManager(AssetHandoverDocumentMediaQueryset)

    class Status(models.TextChoices):
        ACCEPTED = 'accepted', _('Accepted')
        CONTESTED = 'contested', _('Contested')
        IN_PROGRESS = 'in_progress', _('In Progress')
        REMOVED = 'removed', _('Removed')
        REQUESTED_APPROVAL_REJECTED = 'requested_approval_rejected', _('Requested Approval Rejected')
        REQUESTING_APPROVAL = 'requesting_approval', _('Requesting Approval')

    class Meta(BaseModel.Meta):
        db_table = 'asset_handover_document_media'
        constraints = [
            models.UniqueConstraint(
                fields=('asset_handover_document', 'media',),
                name='asset_handover_document_media_unique',
                condition=Q(deleted__isnull=True)
            )
        ]

    asset_handover_document = models.ForeignKey('AssetHandoverDocument', on_delete=models.CASCADE)
    media = models.ForeignKey('Media', on_delete=models.CASCADE)
    uid = models.CharField(max_length=255, null=True, default=None)
    status = models.CharField(choices=Status.choices, max_length=255)
    last_confirmed_update = models.ForeignKey('AssetHandoverDocumentMediaUpdate', on_delete=models.SET_NULL, null=True)
