from api.models import Project
from api.models.location_matrix_package import LocationMatrixPackage
from api.models.location_matrix import LocationMatrix
from api.models.package_matrix import PackageMatrix


def cascade_delete_project_with_related_entities(project_pk: int):
    LocationMatrixPackage.objects.filter(package_matrix__project_id=project_pk).delete()
    LocationMatrix.objects.filter(project_id=project_pk).delete()
    PackageMatrix.objects.filter(project_id=project_pk).delete()
    Project.all_objects.filter(pk=project_pk).delete()
