from django.db.models.signals import post_delete
from django.dispatch import receiver
from safedelete.signals import post_softdelete

from api.models import PackageHandover
from api.queues.handover_document import delete_handover_document_on_package_handover_delete


@receiver(signal=(post_delete, post_softdelete), sender=PackageHandover)
def on_package_handover_delete(sender, instance: PackageHandover, **kwargs):
    if not kwargs.get('raw'):
        delete_handover_document_on_package_handover_delete(instance)
