from rest_framework import fields, serializers
from rest_framework.fields import IntegerField

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.serializers.location_matrix.location_matrix_list_serializer import LocationMatrixListSerializer
from api.http.serializers.project_serializer import ProjectSerializer
from api.http.validators import UniqueTogetherValidator, ExistsValidator
from api.models import LocationMatrix, Project, PackageMatrix, LocationMatrixPackage


class LocationMatrixSerializer(BaseModelSerializer):
    class Meta:
        model = LocationMatrix
        list_serializer_class = LocationMatrixListSerializer
        fields = ('id', 'project', 'building', 'level', 'area', 'created_at', 'updated_at')
        validators = [
            UniqueTogetherValidator(
                queryset=LocationMatrix.objects.all(),
                fields=('project', 'building', 'level', 'area',)
            )
        ]
        expandable_fields = {
            'expanded_project': (ProjectSerializer, {'source': 'project'}),
            'expanded_tasks': ('api.http.serializers.TaskSerializer', {'many': True, 'source': 'task_set'}),
            'expanded_quality_issues': ('api.http.serializers.QualityIssueSerializer', {'many': True, 'source': 'qualityissue_set'}),
            'expanded_location_matrix_packages': ('api.http.serializers.LocationMatrixPackagesSerializer', {'many': True, 'source': 'locationmatrixpackage_set'})
        }

    id = IntegerField(required=False, validators=[ExistsValidator(queryset=LocationMatrix.objects.all())])
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all(), required=True)
    building = fields.CharField(max_length=255, required=True)
    level = fields.CharField(max_length=255, required=True)
    area = fields.CharField(max_length=255, required=True)

    def __init__(self, *args, **kwargs):
        self.parent_id = kwargs.pop('parent_id') if 'parent_id' in kwargs else None
        super().__init__(*args, **kwargs)

    def create(self, validated_data):
        location_matrix = super().create(validated_data)
        self.__create_location_matrix_packages(location_matrix)

        return location_matrix

    def __create_location_matrix_packages(self, location_matrix) -> None:
        project_package_matrix = PackageMatrix.objects.filter(project=location_matrix.project).all()
        location_matrix_packages = list()

        for package_matrix in project_package_matrix:
            location_matrix_package = LocationMatrixPackage(
                location_matrix=location_matrix,
                package_matrix=package_matrix,
                package=package_matrix.package,
                package_activity=package_matrix.package_activity,
                package_activity_name=package_matrix.package_activity.name
            )

            location_matrix_packages.append(location_matrix_package)

        LocationMatrixPackage.objects.bulk_create(location_matrix_packages)
