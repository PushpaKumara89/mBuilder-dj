from rest_framework import fields, serializers
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from api.http.serializers.user.user_serializer import UserSerializer
from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import Project, User
from api.models.edit_mode import EditMode


class EditModeSerializer(BaseModelSerializer):
    class Meta:
        model = EditMode
        fields = ('id', 'project', 'entity', 'entity_id', 'user', 'created_at', 'updated_at',)
        expandable_fields = {
            'expanded_user': (UserSerializer, {'source': 'user'}),
        }

    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all(), required=False)
    entity = fields.CharField(max_length=255, required=False)
    entity_id = fields.CharField(max_length=255, required=False)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)

    def validate(self, attrs):
        if 'entity_id' in attrs and 'entity' not in attrs:
            raise ValidationError({'entity': _('Please specify entity to block.')})

        if all(attr not in attrs for attr in ['project', 'entity', 'entity_id']):
            raise ValidationError({'project': _('Please specify at least project id.')})

        return attrs
