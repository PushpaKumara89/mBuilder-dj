from rest_framework import serializers

from api.http.serializers import PackageSerializer, PackageActivitySerializer, CompanySerializer, MediaSerializer, \
    AssetHandoverDocumentTypeSerializer, PackageHandoverDocumentTypeSerializer
from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import Company, HandoverDocument, Project, Package, PackageActivity, Media


class HandoverDocumentReportSerializer(BaseModelSerializer):
    class Meta:
        model = HandoverDocument
        fields = ('id', 'project', 'building', 'level', 'area',
                  'package', 'package_activity', 'company',
                  'media', 'document_type', 'filename', 'uid',
                  'information', 'file_type', 'entity', 'entity_id')
        expandable_fields = {
            'expanded_package': (PackageSerializer, {'source': 'package'}),
            'expanded_package_activity': (PackageActivitySerializer, {'source': 'package_activity', 'omit': ['package_activity_tasks', 'files']}),
            'expanded_company': (CompanySerializer, {'source': 'company'}),
            'expanded_media': (MediaSerializer, {'source': 'media'}),
            'expanded_document_type': (serializers.SerializerMethodField, {'method_name': 'get_document_type'}),
        }

    building = serializers.CharField(max_length=255, required=True)
    level = serializers.CharField(max_length=255, required=True)
    area = serializers.CharField(max_length=255, required=True)
    filename = serializers.CharField(max_length=255, required=True)
    file_type = serializers.CharField(read_only=True)
    uid = serializers.CharField(max_length=255, allow_null=True, required=False)
    information = serializers.CharField(max_length=255, allow_null=True, required=False)
    document_type = serializers.IntegerField(required=True)
    entity = serializers.ChoiceField(required=True, choices=HandoverDocument.Entities.choices)
    entity_id = serializers.IntegerField(required=True)

    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all(), required=True)
    package = serializers.PrimaryKeyRelatedField(queryset=Package.objects.all(), required=True)
    package_activity = serializers.PrimaryKeyRelatedField(queryset=PackageActivity.objects.all(), required=True)
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all(), required=True)
    media = serializers.PrimaryKeyRelatedField(queryset=Media.objects.all(), required=True)

    def get_document_type(self, obj: HandoverDocument) -> dict:
        if obj.is_asset_handover_entity:
            document_type = self.context['asset_handover_document_types'].filter(id=obj.document_type).get()
            return AssetHandoverDocumentTypeSerializer(document_type).data
        else:
            document_type = self.context['package_handover_document_types'].filter(id=obj.document_type).get()
            return PackageHandoverDocumentTypeSerializer(document_type).data
