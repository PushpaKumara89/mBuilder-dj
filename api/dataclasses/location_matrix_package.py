import dataclasses

from api.models import LocationMatrixPackage, User


@dataclasses.dataclass(frozen=True)
class LocationMatrixPackageSyncParams:
    location_matrix_package: LocationMatrixPackage
    updated_location_matrix_package: dict
    user: User
