from rest_framework import fields
from rest_framework.validators import UniqueValidator

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import PackageHandoverDocumentGroup


class PackageHandoverDocumentGroupSerializer(BaseModelSerializer):
    class Meta:
        model = PackageHandoverDocumentGroup
        fields = ('id', 'name',)

    name = fields.CharField(max_length=255, required=True, validators=[
        UniqueValidator(queryset=PackageHandoverDocumentGroup.objects.all())
    ])
