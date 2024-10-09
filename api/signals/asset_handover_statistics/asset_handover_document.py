from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from api.models import AssetHandoverDocument
from api.queues.asset_handover_statistics import update_statistics_on_document_update, \
    create_statistics_on_asset_handover_document_create


@receiver(signal=post_save, sender=AssetHandoverDocument)
def on_asset_handover_document_create(sender, instance: AssetHandoverDocument, **kwargs):
    if kwargs.get('created', False) and not kwargs.get('raw', False):
        transaction.on_commit(lambda : create_statistics_on_asset_handover_document_create(instance))


@receiver(post_save, sender=AssetHandoverDocument)
def on_asset_handover_document_update(sender, instance: AssetHandoverDocument, **kwargs):
    def is_number_required_files_changed():
        return not kwargs.get('created', False) and \
               not kwargs.get('raw', False) and \
               kwargs.get('update_fields') and \
               'number_required_files' in kwargs['update_fields']

    if is_number_required_files_changed():
        update_statistics_on_document_update(instance)
