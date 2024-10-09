from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField
from rest_framework.validators import UniqueValidator
from typing import Union, Optional, Dict

from api.http.serializers.package_handover.package_handover_serializer import PackageHandoverSerializer
from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.serializers.package_activity_tasks import PackageActivityTaskSerializer
from api.models import PackageActivity, PackageMatrixHiddenActivityTask, Project, Media


class PackageActivitySerializer(BaseModelSerializer):
    project_id = None

    class Meta:
        fields = ('id', 'name', 'activity_id', 'package_activity_tasks', 'files', 'description', 'description_image',)
        model = PackageActivity
        expandable_fields = {
            'expanded_package_activity_tasks': (
                PackageActivityTaskSerializer, {'source': 'packageactivitytask_set', 'many': True},
            ),
            'expanded_modified': (serializers.SerializerMethodField, {'method_name': 'is_modified'}),
            'expanded_projects_count': (serializers.SerializerMethodField, {'method_name': 'projects_count'}),
            'expanded_files': ('api.http.serializers.MediaSerializer', {'many': True, 'source': 'files'}),
            'expanded_files_count': (serializers.SerializerMethodField, {'method_name': 'files_count'}),
            'expanded_can_add_asset_handovers': (serializers.SerializerMethodField, {'method_name': 'can_add_asset_handovers'}),
            'expanded_package_handover': (serializers.SerializerMethodField, {'method_name': 'get_package_handover'}),
            'expanded_description': (serializers.CharField, {'source': 'description'}),
            'expanded_description_image': ('api.http.serializers.MediaSerializer', {'source': 'description_image'})
        }

    name = CharField(required=True, validators=[
        UniqueValidator(
            queryset=PackageActivity.objects.all(),
            message=_('A package activity with this name already exists.'),
            lookup='iexact'
        )
    ])
    activity_id = CharField(max_length=255, required=False, allow_null=True)
    package_activity_tasks = PackageActivityTaskSerializer(source='packageactivitytask_set', required=True, many=True)
    files = serializers.PrimaryKeyRelatedField(queryset=Media.objects.all(), required=False, many=True)
    description = serializers.CharField(write_only=True, required=False, allow_null=True, allow_blank=True)
    description_image = serializers.PrimaryKeyRelatedField(queryset=Media.objects.all(), write_only=True, required=False, allow_null=True)

    def __init__(self, *args, **kwargs) -> None:
        self.project_id = kwargs.pop('project_id', None)
        super().__init__(*args, **kwargs)

    def get_package_handover(self, obj: PackageActivity) -> Optional[Dict]:
        package_matrix = obj.packagematrix_set.first()

        if package_matrix:
            return PackageHandoverSerializer(package_matrix.packagehandover_set.first()).data

        return None

    def validate_package_activity_tasks(self, activity_tasks):
        descriptions = [item['description'] for item in activity_tasks]
        is_default_for_subtask = [item.get('is_default_for_subtask') for item in activity_tasks]
        errors = []

        self._check_duplications(descriptions, errors, 'description')
        self._check_duplications(is_default_for_subtask, errors, 'is_default_for_subtask')

        has_errors = len(list(filter(lambda error: len(error) > 0, errors))) > 0

        if has_errors:
            raise ValidationError(errors, code='unique')

        return activity_tasks

    @staticmethod
    def _check_duplications(fields: list, errors: list, name: str) -> None:
        messages = {
            'description': _('A task description is duplicated.'),
            'is_default_for_subtask': _('A task is_default_for_subtask is enabled for few tasks at the same time.')
        }

        for index, field in enumerate(fields):
            if field and fields.count(field) > 1:
                errors.append({name: messages[name]})
            else:
                errors.append({})

    def is_modified(self, obj) -> bool:
        project_id = self.get_project_id()
        return PackageMatrixHiddenActivityTask.objects.filter(
            package_activity_task__package_activity=obj.pk,
            package_matrix__project__pk=project_id
        ).exists()

    def projects_count(self, obj) -> int:
        if hasattr(obj, 'not_deleted_packagematrix_set'):
            return len(obj.not_deleted_packagematrix_set)

        pk = obj['id'] if type(obj) is dict else obj.id
        return Project.objects.filter(
            packagematrix__deleted__isnull=True,
            packagematrix__package__deleted__isnull=True,
            packagematrix__package_activity__pk=pk,
            deleted__isnull=True
        ).count()

    def files_count(self, obj: PackageActivity) -> int:
        return obj.files.count()

    def can_add_asset_handovers(self, obj: PackageActivity) -> bool:
        project_id = self.get_project_id()

        if project_id:
            enabled_location_matrix_packages_count = obj.get_enabled_location_matrix_packages_count(project_id)
            asset_handover_count = obj.get_asset_handover_count(project_id)
            return enabled_location_matrix_packages_count > asset_handover_count

        return True

    def get_project_id(self) -> Union[int, str]:
        is_project_pk_in_context = 'view' in self.context and 'project_pk' in self.context['view'].kwargs
        return self.context['view'].kwargs['project_pk'] if is_project_pk_in_context else self.project_id
