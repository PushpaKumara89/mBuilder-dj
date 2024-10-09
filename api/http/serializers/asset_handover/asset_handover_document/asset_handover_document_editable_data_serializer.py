from rest_framework import serializers

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import AssetHandoverDocument, AssetHandoverDocumentType


class AssetHandoverDocumentEditableDataSerializer(BaseModelSerializer):
    class Meta:
        model = AssetHandoverDocument
        fields = ('id', 'document_type', 'number_required_files',)

    document_type = serializers.PrimaryKeyRelatedField(required=True, queryset=AssetHandoverDocumentType.objects.all())
    number_required_files = serializers.IntegerField(required=False)
