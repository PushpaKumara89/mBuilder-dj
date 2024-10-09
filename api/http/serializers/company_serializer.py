from django.db.models import Q
from django.utils.translation import gettext as _
from rest_framework import fields, serializers
from rest_framework.validators import UniqueValidator

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import Company


class CompanySerializer(BaseModelSerializer):
    class Meta:
        model = Company
        fields = ('id', 'name', 'assigned_to_activity', 'created_at', 'updated_at')
        expandable_fields = {
            'expanded_users_count': (serializers.SerializerMethodField, {'method_name': 'get_users_count'})
        }

    name = fields.CharField(max_length=255,
                            required=True,
                            validators=[
                                UniqueValidator(queryset=Company.objects.all(),
                                                message=_('A company with this name already exists.'),
                                                lookup='iexact')
                            ])

    assigned_to_activity = fields.BooleanField(read_only=True)

    def get_users_count(self, obj: Company):
        return obj.user_set.filter(deleted__isnull=True, is_active=True).count()
