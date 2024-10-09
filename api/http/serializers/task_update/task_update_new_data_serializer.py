from rest_framework import fields
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import Task


class TaskUpdateNewDataSerializer(BaseModelSerializer):
    class Meta:
        model = Task
        fields = ('status', 'local_id',)

    status = fields.ChoiceField(choices=Task.Statuses.choices, required=False, allow_blank=False, allow_null=False)
    local_id = fields.CharField(required=False, allow_null=True, allow_blank=True)

    def validate(self, data):
        if hasattr(self, 'initial_data'):
            unknown_keys = set(self.initial_data.keys()) - set(self.fields.keys())

            if unknown_keys:
                raise ValidationError(_('Got unknown fields: {}'.format(unknown_keys)))

        return data
