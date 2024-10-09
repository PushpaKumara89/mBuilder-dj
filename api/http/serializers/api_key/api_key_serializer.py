from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.http.serializers import ProjectSerializer, CompanySerializer
from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import ApiKey, Project, Company, User


class ApiKeySerializer(BaseModelSerializer):
    class Meta:
        model = ApiKey
        fields = ('id', 'token', 'created_at', 'updated_at', 'project', 'company', 'expires_at',
                  'has_access_to_project', 'has_access_to_package_handover', 'has_access_to_asset_handover',
                  'has_access_to_quality_issue')
        expandable_fields = {
            'expanded_project': (ProjectSerializer, {'source': 'project'}),
            'expanded_company': (CompanySerializer, {'source': 'company'}),
        }

    token = serializers.UUIDField(read_only=True)
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all(), required=True)
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all(), required=True)
    expires_at = serializers.DateField(required=True)
    has_access_to_project = serializers.BooleanField(required=False)
    has_access_to_package_handover = serializers.BooleanField(required=False)
    has_access_to_asset_handover = serializers.BooleanField(required=False)
    has_access_to_quality_issue = serializers.BooleanField(required=False)

    def validate(self, data: dict):
        def company_belongs_to_project_clients():
            project = data['project'] if 'project' in data else self.instance.project
            company = data['company'] if 'company' in data else self.instance.company

            return project.users.filter(
                company=company,
                group=User.Group.CLIENT.value
            ).exists()

        if not company_belongs_to_project_clients():
            raise ValidationError(_('Users from this company don\'t exists in the project.'))

        return data
