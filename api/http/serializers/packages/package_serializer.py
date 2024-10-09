from rest_framework import serializers
from rest_framework.serializers import IntegerField, CharField

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.validators import ExistsValidator
from api.http.validators.unique_or_unique_except import UniqueOrUniqueExceptValidator
from api.models import Package, Project


class PackageSerializer(BaseModelSerializer):
    class Meta:
        model = Package
        fields = ('id', 'name', 'created_at', 'updated_at', 'order')
        expandable_fields = {
            'expanded_package_activities': ('api.http.serializers.package_activity.package_activity_serializer.PackageActivitySerializer', {'many': True, 'source': 'package_activities'}),
            'expanded_projects_count': (serializers.SerializerMethodField, {'method_name': 'projects_count'})
        }

    id = IntegerField(required=False, validators=[ExistsValidator(queryset=Package.objects.all())])
    name = CharField(required=True, max_length=255, validators=[
        UniqueOrUniqueExceptValidator(queryset=Package.objects.all(), lookup='iexact')
    ])
    order = IntegerField(required=True)

    def projects_count(self, obj):
        if hasattr(obj, 'not_deleted_packagematrix_set'):
            return len(obj.not_deleted_packagematrix_set)

        package_pk = obj['id'] if isinstance(obj, dict) else obj.id
        return Project.objects.filter(
            packagematrix__deleted__isnull=True,
            packagematrix__package_activity__deleted__isnull=True,
            packagematrix__package__pk=package_pk,
            deleted__isnull=True
        ).distinct().count()
