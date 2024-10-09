from django.db.models.signals import post_save
from django.dispatch import receiver

from api.models import PackageActivity, LocationMatrixPackage


@receiver(post_save, sender=PackageActivity)
def package_activity_post_save(sender, instance, **kwargs):
    if not kwargs.get('created', False) and not kwargs.get('raw', False):
        location_matrix_packages = LocationMatrixPackage.objects.filter(package_matrix__package_activity=instance.pk)

        location_matrix_packages.update(package_activity_name=instance.name)
