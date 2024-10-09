from django.db.models.signals import post_delete
from django.dispatch import receiver
from safedelete.signals import post_softdelete, post_undelete

from api.models import PackageHandover
from api.queues.package_handover_statistics import delete_statistics_on_package_handover_delete, \
    undelete_statistics_on_package_handover_undelete


@receiver(signal=(post_delete, post_softdelete), sender=PackageHandover)
def on_package_handover_delete(sender, instance: PackageHandover, **kwargs) -> None:
    delete_statistics_on_package_handover_delete(instance)


@receiver(signal=post_undelete, sender=PackageHandover)
def on_package_handover_undelete(sender, instance: PackageHandover, **kwargs) -> None:
    undelete_statistics_on_package_handover_undelete(instance)
