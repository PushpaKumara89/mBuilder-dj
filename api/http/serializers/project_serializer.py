from typing import Optional, Dict

from django.utils.translation import gettext as _
from djmoney.contrib.django_rest_framework import MoneyField
from rest_framework import fields, serializers
from rest_framework.exceptions import PermissionDenied
from rest_framework.validators import UniqueValidator

from api.http.serializers.project_news_serializer import ProjectNewsSerializer
from api.http.serializers.user.user_serializer import UserSerializer
from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.serializers.media.media_serializer import MediaSerializer
from api.http.validators import DateAfterValidator
from api.models import Project, Media


class ProjectSerializer(BaseModelSerializer):
    class Meta:
        model = Project
        fields = (
            'id', 'name', 'number', 'image', 'image_id', 'status', 'start_date', 'created_at', 'updated_at', 'value',
            'completion_date', 'show_estimated_man_hours', 'is_task_visible_for_clients', 'value_currency',
            'is_subtask_visible_for_clients'
        )
        expandable_fields = {
            'expanded_news': (ProjectNewsSerializer, {'many': True, 'source': 'projectnews_set'}),
            'expanded_key_contacts': (UserSerializer, {'many': True, 'source': 'key_contacts'}),
            'expanded_response_categories': (serializers.SerializerMethodField, {'method_name': 'get_response_categories'}),
        }

    id = fields.ReadOnlyField()
    name = fields.CharField(required=True, max_length=255, validators=[
        UniqueValidator(queryset=Project.objects.all(),
                        lookup='iexact',
                        message=_('A project with this name already exists.'))
    ])
    number = fields.CharField(required=True, max_length=255, validators=[
        UniqueValidator(queryset=Project.objects.all(),
                        lookup='iexact',
                        message=_('A project with this number already exists.'))
    ])
    image = MediaSerializer(required=False, read_only=True)
    status = fields.ChoiceField(choices=Project.Status.choices)
    image_id = serializers.PrimaryKeyRelatedField(required=False, write_only=True, queryset=Media.objects.all(),
                                                  allow_null=True)
    start_date = fields.DateField(required=True)
    completion_date = fields.DateField(required=True)
    show_estimated_man_hours = fields.BooleanField(required=False)
    value = MoneyField(required=True, max_digits=12, decimal_places=2, default_currency='USD')

    def get_action(self) -> Optional[str]:
        if 'request' not in self.context:
            return None

        if hasattr(self.context['request'].parser_context['view'], 'action'):
            return self.context['request'].parser_context['view'].action

        return None

    def get_fields(self):
        fields_ = super().get_fields()
        if self.get_action() in ('list', 'retrieve',):
            user = self.context['request'].user
            if not (user.is_company_admin or user.is_manager or user.is_admin):
                fields_.pop('completion_date', None)
        return fields_

    def validate(self, data: Dict):
        DateAfterValidator(start_date='start_date', date_after='completion_date')(data, self)

        if self._is_user_cannot_change_is_subtask_visible_for_client(data):
            raise PermissionDenied()

        return data

    @staticmethod
    def get_response_categories(project: Project):
        from api.http.serializers import ResponseCategorySerializer

        response_categories = ResponseCategorySerializer(project.responsecategory_set.all(), many=True)
        return sorted(response_categories.data, key=lambda response_category: response_category['name'])

    def _is_user_cannot_change_is_subtask_visible_for_client(self, validated_data: Dict):
        is_task_visible_for_clients = validated_data.get('is_task_visible_for_clients')

        if self.instance:
            return is_task_visible_for_clients is not None \
                and self.instance.id \
                and self.instance.is_task_visible_for_clients != is_task_visible_for_clients \
                and not self.context['request'].user.is_company_admin

        return is_task_visible_for_clients is not None \
            and not is_task_visible_for_clients \
            and not self.context['request'].user.is_company_admin
