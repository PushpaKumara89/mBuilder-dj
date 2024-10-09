from rest_framework import serializers

from api.http.serializers import BaseModelSerializer
from api.models import HandoverDocument


class HandoverDocumentMediaBatchDownloadSerializer(BaseModelSerializer):
    class Meta:
        model = HandoverDocument
        fields = ('handover_document',)

    handover_document = serializers.PrimaryKeyRelatedField(queryset=HandoverDocument.objects.all(), many=True)
