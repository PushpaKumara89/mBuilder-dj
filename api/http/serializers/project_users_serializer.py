from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import Project, User, QualityIssue


class ProjectUsersSerializer(BaseModelSerializer):
    class Meta:
        model = Project
        fields = ('users',)

    users = serializers.PrimaryKeyRelatedField(required=True, queryset=User.objects.all(), many=True)

    def validate_users(self, users: list):
        def does_client_has_active_quality_issues():
            return (user.is_client or user.is_consultant) and \
                   QualityIssue.objects.filter(~Q(status__in=[QualityIssue.Status.CLOSED, QualityIssue.Status.REMOVED]),
                                               user=user, location_matrix__project=self.instance).exists()

        for user in users:
            if does_client_has_active_quality_issues():
                raise ValidationError(_('You cannot remove %s %s with active quality issues.' %
                                        ('client' if user.is_client else 'consultant', user.email, )))

        return users
