from django.utils.translation import gettext as _
from rest_framework import fields
from rest_framework.validators import UniqueValidator

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import AssetHandoverDocumentType


class AssetHandoverDocumentTypeSerializer(BaseModelSerializer):
    class Meta:
        model = AssetHandoverDocumentType
        fields = ('id', 'name', 'created_at', 'updated_at')

    name = fields.CharField(max_length=255,
                            required=True,
                            validators=[
                                UniqueValidator(queryset=AssetHandoverDocumentType.objects.all(),
                                                message=_('A type with this name already exists.'),
                                                lookup='iexact')
                            ])
