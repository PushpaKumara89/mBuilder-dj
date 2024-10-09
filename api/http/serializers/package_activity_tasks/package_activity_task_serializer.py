from rest_framework import fields, serializers

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.validators import ExistsValidator, UniqueTogetherValidator
from api.models import PackageActivityTask, PackageActivity, PackageMatrixHiddenActivityTask


class PackageActivityTaskSerializer(BaseModelSerializer):
    class Meta:
        fields = (
            'id', 'description', 'is_not_applicable_status_by_default', 'is_photo_required',
            'order', 'package_activity', 'photo_requirement_comment', 'is_default_for_subtask',
        )
        model = PackageActivityTask
        expandable_fields = {
            'expanded_hidden': (serializers.SerializerMethodField, {'method_name': 'is_hidden'})
        }

        validators: [
            UniqueTogetherValidator(
                fields=['description', 'package_activity'], queryset=PackageActivityTask.objects.all(),
                lookup='iexact'
            )
        ]

    id = fields.IntegerField(required=False, validators=[ExistsValidator(queryset=PackageActivityTask.objects.all())])
    description = fields.CharField(required=True, max_length=None)
    is_not_applicable_status_by_default = fields.BooleanField(required=False)
    is_photo_required = fields.BooleanField(required=False)
    order = fields.IntegerField(required=True)
    photo_requirement_comment = fields.CharField(required=True, max_length=None)
    package_activity = serializers.PrimaryKeyRelatedField(queryset=PackageActivity.objects.all(), required=False)
    is_default_for_subtask = serializers.BooleanField(required=False)

    def is_hidden(self, obj) -> bool:
        if hasattr(self.parent, 'parent') and hasattr(self.parent.parent, 'project_id'):
            return PackageMatrixHiddenActivityTask.objects.filter(
                package_activity_task=obj.pk,
                package_matrix__project=self.parent.parent.project_id
            ).exists()
        return False
