from rest_framework import serializers

from api.http.serializers import BaseModelSerializer
from api.models import AssetHandoverDocumentMedia


class AssetHandoverDocumentMediaBatchDownloadSerializer(BaseModelSerializer):
    class Meta:
        model = AssetHandoverDocumentMedia
        fields = ('asset_handover_document_media',)

    asset_handover_document_media = serializers.PrimaryKeyRelatedField(queryset=AssetHandoverDocumentMedia.objects.all(), many=True)
