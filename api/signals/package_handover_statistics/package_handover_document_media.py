from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from safedelete.signals import post_softdelete

from api.models import PackageHandoverDocumentMedia
from api.queues.package_handover_statistics import decrease_statistics_for_document_media_status, \
    increase_statistics_for_document_media_status, update_statistics_by_statuses_on_document_media_status_change


@receiver(signal=post_save, sender=PackageHandoverDocumentMedia)
def on_package_handover_document_media_post_save(sender, instance: PackageHandoverDocumentMedia, **kwargs):
    if kwargs.get('created', False) and not kwargs.get('raw', False):
        increase_statistics_for_document_media_status(instance)

    if not kwargs.get('created', False) and not kwargs.get('raw', False) and kwargs.get('update_fields'):
        def status_in_update_fields():
            return kwargs['update_fields'] and 'status' in kwargs['update_fields']

        def is_status_changed():
            return status_in_update_fields() \
                and hasattr(instance, 'update_fields_original_values') \
                and 'status' in instance.update_fields_original_values \
                and instance.update_fields_original_values['status'] != instance.status

        if is_status_changed():
            update_statistics_by_statuses_on_document_media_status_change(instance)


@receiver(signal=(post_delete, post_softdelete), sender=PackageHandoverDocumentMedia)
def on_package_handover_document_media_post_delete(sender, instance: PackageHandoverDocumentMedia, **kwargs):
    if not kwargs.get('raw', False):
        decrease_statistics_for_document_media_status(instance)
