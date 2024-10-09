from django.db.models.signals import post_delete
from django.dispatch import receiver
from safedelete.signals import post_undelete, post_softdelete

from api.models import PackageMatrix
from api.queues.asset_handover_statistics import delete_statistics_on_package_matrix_delete, \
    undelete_statistics_on_package_matrix_undelete


@receiver((post_delete, post_softdelete), sender=PackageMatrix)
def on_package_matrix_delete(sender, instance: PackageMatrix, **kwargs):
    if not kwargs.get('raw', False):
        delete_statistics_on_package_matrix_delete(instance)


@receiver(post_undelete, sender=PackageMatrix)
def on_package_matrix_undelete(sender, instance: PackageMatrix, **kwargs):
    if not kwargs.get('raw', False):
        undelete_statistics_on_package_matrix_undelete(instance)
