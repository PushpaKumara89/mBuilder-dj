from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.http.serializers import UserSerializer, BaseModelSerializer, MediaSerializer, SubtaskSerializer
from api.http.serializers.task import TaskSerializer
from api.models import Subtask, Task, User, QualityIssue, Company


class SubtaskBulkCreateFromQualityIssueSerializer(BaseModelSerializer):
    class Meta:
        model = Subtask
        fields = (
            'id', 'task', 'user', 'company', 'quality_issues',
        )
        expandable_fields = {
            'expanded_task': (TaskSerializer, {'source': 'task'}),
            'expanded_company': (TaskSerializer, {'source': 'company'}),
            'expanded_user': (UserSerializer, {'source': 'user'}),
            'expanded_files': (MediaSerializer, {'many': True, 'source': 'files'})
        }

    task = serializers.PrimaryKeyRelatedField(queryset=Task.objects.all(), required=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)
    quality_issues = serializers.PrimaryKeyRelatedField(queryset=QualityIssue.objects.all(), required=True, many=True)
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all(), required=False, allow_null=True, default=None)

    def validate_quality_issues(self, data):
        qi_location_matrices_without_tasks = list(QualityIssue.objects.filter(pk__in=[qi.id for qi in data],
                                                                              location_matrix__task__isnull=True
                                                                              ).values_list('id', flat=True))

        if qi_location_matrices_without_tasks:
            raise ValidationError(
                'The following Quality Issue(s) are unable to be assigned to the location you have selected: %s'
                % ', '.join([f'QI-{qi_id}' for qi_id in qi_location_matrices_without_tasks]))

        if Subtask.objects.filter(quality_issue__in=data).exists():
            raise ValidationError(
                'Subtask for the one of the selected quality issue already exists.'
            )

        return data
