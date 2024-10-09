from django.db.models.signals import post_delete
from django.dispatch import receiver
from safedelete.signals import post_softdelete

from api.models import AssetHandoverDocumentMedia
from api.queues.handover_document import delete_handover_document_on_asset_handover_document_media_delete


@receiver(signal=(post_delete, post_softdelete), sender=AssetHandoverDocumentMedia)
def on_asset_handover_document_media_delete(sender, instance: AssetHandoverDocumentMedia, **kwargs):
    delete_handover_document_on_asset_handover_document_media_delete(instance)
