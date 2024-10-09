from rest_framework import serializers

from api.http.serializers.packages.package_serializer import PackageSerializer
from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.serializers.project_serializer import ProjectSerializer
from api.http.validators import UniqueTogetherValidator
from api.models import Project, PackageMatrix, Package, PackageActivity, LocationMatrix, LocationMatrixPackage
from api.queues.package_handover import create_or_restore_package_handover
from api.queues.restore_tasks_related_to_reinstated_package_matrix import restore_tasks_related_to_reinstated_package_matrix


class PackageMatrixSerializer(BaseModelSerializer):
    class Meta:
        model = PackageMatrix
        fields = ('project', 'package', 'package_activity', 'id',)
        validators = [
            UniqueTogetherValidator(
                queryset=PackageMatrix.objects.all(),
                fields=('project', 'package', 'package_activity',)
            )
        ]
        expandable_fields = {
            'expanded_package_activity': ('api.http.serializers.package_activity.package_activity_serializer.PackageActivitySerializer', {'source': 'package_activity'}),
            'expanded_project': (ProjectSerializer, {'source': 'project'}),
            'expanded_package': (PackageSerializer, {'source': 'package'}),
            'expanded_companies': ('api.http.serializers.CompanySerializer', {'many': True, 'source': 'companies'})
        }

    project = serializers.PrimaryKeyRelatedField(required=True, queryset=Project.objects.all())
    package = serializers.PrimaryKeyRelatedField(required=True, queryset=Package.objects.all())
    package_activity = serializers.PrimaryKeyRelatedField(required=True, queryset=PackageActivity.objects.all())

    def __init__(self, *args, **kwargs):
        self.project_id = kwargs.pop('project_id', None)
        super().__init__(*args, **kwargs)

    def create(self, validated_data):
        project = validated_data['project']
        package = validated_data['package']
        package_activity = validated_data['package_activity']
        package_matrix = PackageMatrix.all_objects.filter(project_id=project, package_activity_id=package_activity,
                                                          package_id=package).first()
        if package_matrix and package_matrix.deleted:
            package_matrix.undelete()
        elif not package_matrix:
            package_matrix = PackageMatrix.objects.create(project_id=project, package_activity_id=package_activity,
                                                          package_id=package)
        self.__create_location_matrix_packages(package_matrix)

        create_or_restore_package_handover([package_matrix])

    def __create_location_matrix_packages(self, package_matrix) -> None:
        project_location_matrix_list = LocationMatrix.objects.filter(project=package_matrix.project).all()
        new_location_matrix_packages = list()

        for location_matrix in project_location_matrix_list:
            package_activity = package_matrix.package_activity

            lmp = LocationMatrixPackage.all_objects.filter(
                location_matrix=location_matrix,
                package_activity=package_activity,
            ).first()

            if lmp and not lmp.deleted:
                LocationMatrixPackage.objects.filter(
                    location_matrix=location_matrix,
                    package_activity=package_activity,
                ).update(
                    package_matrix=package_matrix,
                    package=package_matrix.package,
                )
            elif lmp and lmp.deleted:
                LocationMatrixPackage.deleted_objects.filter(
                    location_matrix=location_matrix,
                    package_activity=package_activity,
                ).update(
                    deleted=None,
                    package_matrix=package_matrix,
                    package=package_matrix.package,
                )

                enabled_location_matrix_packages = LocationMatrixPackage.objects.filter(
                    location_matrix=location_matrix,
                    package_activity=package_activity,
                    enabled=True
                ).all()

                restore_tasks_related_to_reinstated_package_matrix(
                    package_activity, enabled_location_matrix_packages, location_matrix, self.context['request'].user
                )
            elif not lmp:
                location_matrix_package = LocationMatrixPackage(
                    location_matrix=location_matrix,
                    package_matrix=package_matrix,
                    package=package_matrix.package,
                    package_activity=package_matrix.package_activity,
                    package_activity_name=package_matrix.package_activity.name
                )

                new_location_matrix_packages.append(location_matrix_package)

        LocationMatrixPackage.objects.bulk_create(new_location_matrix_packages)
