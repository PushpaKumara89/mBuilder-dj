from django.db.models.signals import post_delete
from django.dispatch import receiver
from safedelete.signals import post_softdelete, post_undelete

from api.models import AssetHandover
from api.queues.handover_document import delete_handover_document_on_asset_handover_delete, \
    undelete_handover_document_on_asset_handover_undelete


@receiver(signal=(post_delete, post_softdelete), sender=AssetHandover)
def on_asset_handover_delete(sender, instance: AssetHandover, **kwargs):
    delete_handover_document_on_asset_handover_delete(instance)


@receiver(signal=post_undelete, sender=AssetHandover)
def on_asset_handover_undelete(sender, instance: AssetHandover, **kwargs):
    undelete_handover_document_on_asset_handover_undelete([instance])
