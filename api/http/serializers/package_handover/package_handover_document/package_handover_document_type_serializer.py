from rest_framework import fields, serializers
from rest_framework.validators import UniqueValidator

from api.http.serializers.package_handover.package_handover_document import PackageHandoverDocumentGroupSerializer
from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import PackageHandoverDocumentType, PackageHandoverDocumentGroup


class PackageHandoverDocumentTypeSerializer(BaseModelSerializer):
    class Meta:
        model = PackageHandoverDocumentType
        fields = ('id', 'name', 'group')
        expandable_fields = {
            'expanded_group': (PackageHandoverDocumentGroupSerializer, {'source': 'group'})
        }

    name = fields.CharField(max_length=255, required=True, validators=[
        UniqueValidator(queryset=PackageHandoverDocumentType.objects.all())
    ])
    group = serializers.PrimaryKeyRelatedField(queryset=PackageHandoverDocumentGroup.objects.all(), required=True)
