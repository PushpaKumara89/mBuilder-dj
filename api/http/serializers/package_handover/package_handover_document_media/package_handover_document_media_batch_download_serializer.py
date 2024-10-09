from rest_framework import serializers

from api.http.serializers import BaseModelSerializer
from api.models import PackageHandoverDocumentMedia


class PackageHandoverDocumentMediaBatchDownloadSerializer(BaseModelSerializer):
    class Meta:
        model = PackageHandoverDocumentMedia
        fields = ('package_handover_document_media',)

    package_handover_document_media = serializers.PrimaryKeyRelatedField(queryset=PackageHandoverDocumentMedia.objects.all(), many=True)
