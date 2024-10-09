from django.db import models
from safedelete import SOFT_DELETE

from api.models.base_model import BaseModel
from api.models.media import Media


class LocationMatrixPackage(BaseModel):
    create_events_on_update = True

    _safedelete_policy = SOFT_DELETE

    class Meta(BaseModel.Meta):
        db_table = 'location_matrix_packages'
        constraints = [
            models.UniqueConstraint(
                fields=['location_matrix', 'package_matrix'],
                name='location_matrix_packages_uniqueness',
                condition=models.Q(deleted__isnull=True)
            ),
            models.Index(
                fields=('location_matrix', 'enabled'),
                condition=models.Q(deleted__isnull=True),
                name='location_matrix_packages_location_matrix_enabled_index'
            )
        ]

    location_matrix = models.ForeignKey('LocationMatrix', on_delete=models.CASCADE)
    package_matrix = models.ForeignKey('PackageMatrix', on_delete=models.CASCADE)
    enabled = models.BooleanField(default=False)

    media = models.ManyToManyField(Media)

    package = models.ForeignKey('Package', on_delete=models.CASCADE)
    package_activity = models.ForeignKey('PackageActivity', on_delete=models.CASCADE)
    package_activity_name = models.CharField(max_length=255)
