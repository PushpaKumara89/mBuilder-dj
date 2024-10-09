from enum import Enum

from django.utils.translation import gettext as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import PackageActivityTask, PackageMatrix, PackageMatrixHiddenActivityTask


class PackageMatrixHiddenActivityTaskSerializer(BaseModelSerializer):
    class Action(Enum):
        HIDE = 0
        SHOW = 1

    action: Action

    class Meta:
        model = PackageMatrixHiddenActivityTask
        fields = ('package_matrix', 'package_activity_task',)

    package_matrix = serializers.PrimaryKeyRelatedField(queryset=PackageMatrix.objects.all())
    package_activity_task = serializers.PrimaryKeyRelatedField(queryset=PackageActivityTask.objects.all())

    def __init__(self, *args, action: Action = None, **kwargs):
        self.action = action
        super().__init__(*args, **kwargs)

    def validate(self, attrs):
        if self.action == self.Action.HIDE:
            is_package_activity_task_already_hidden = self.Meta.model.objects.filter(
                package_matrix=attrs['package_matrix'],
                package_activity_task=attrs['package_activity_task']
            ).exists()

            if is_package_activity_task_already_hidden:
                raise ValidationError(_('This package activity task already hidden.'))
        else:
            is_package_activity_task_already_shown = not self.Meta.model.objects.filter(
                package_matrix=attrs['package_matrix'],
                package_activity_task=attrs['package_activity_task']
            ).exists()

            if is_package_activity_task_already_shown:
                raise ValidationError(_('This package activity task already shown.'))

        return attrs
