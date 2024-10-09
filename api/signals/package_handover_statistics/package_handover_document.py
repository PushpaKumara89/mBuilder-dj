from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from safedelete.signals import post_softdelete, post_undelete

from api.models import PackageHandoverDocument
from api.queues.package_handover_statistics import delete_statistics_on_package_handover_document_delete, \
    undelete_statistics_on_package_handover_document_undelete, create_statistics_on_package_handover_document_create


@receiver(signal=post_save, sender=PackageHandoverDocument)
def on_package_handover_document_create(sender, instance: PackageHandoverDocument, **kwargs):
    if kwargs.get('created', False) and not kwargs.get('raw', False):
        transaction.on_commit(lambda : create_statistics_on_package_handover_document_create(instance))


@receiver(signal=(post_delete, post_softdelete), sender=PackageHandoverDocument)
def on_package_handover_document_delete(sender, instance: PackageHandoverDocument, **kwargs) -> None:
    delete_statistics_on_package_handover_document_delete(instance)


@receiver(signal=post_undelete, sender=PackageHandoverDocument)
def on_package_handover_document_undelete(sender, instance: PackageHandoverDocument, **kwargs) -> None:
    undelete_statistics_on_package_handover_document_undelete(instance)
