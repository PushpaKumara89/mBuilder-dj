from rest_framework import fields, serializers

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.serializers.package_handover.package_handover_statistics.package_handover_statistics_aggregation_serializer import \
    PackageHandoverStatisticsAggregationSerializer
from api.models import PackageHandover, PackageHandoverDocumentType, PackageHandoverDocument, Project, PackageActivity


class PackageHandoverDocumentSerializer(BaseModelSerializer):
    class Meta:
        model = PackageHandoverDocument
        fields = ('id', 'package_handover', 'package_handover_document_type', 'number_required_files',
                  'project', 'package_activity')
        expandable_fields = {
            'expanded_package_handover_document_media': (
                'api.http.serializers.PackageHandoverDocumentMediaSerializer',
                {'many': True, 'source': 'packagehandoverdocumentmedia_set'}
            ),
            'expanded_package_handover_document_type': (
                'api.http.serializers.package_handover.package_handover_document.PackageHandoverDocumentTypeSerializer',
                {'source': 'package_handover_document_type'}
            ),
            'expanded_package_handover_statistics': (PackageHandoverStatisticsAggregationSerializer, {'source': 'packagehandoverstatistics_set', 'many': True}),
            'expanded_package_activity': ('api.http.serializers.PackageActivityShortSerializer', {'source': 'package_activity'})
        }

    package_handover = serializers.PrimaryKeyRelatedField(queryset=PackageHandover.objects.all(), required=True)
    package_handover_document_type = serializers.PrimaryKeyRelatedField(queryset=PackageHandoverDocumentType.objects.all(), required=True)
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all(), required=True)
    package_activity = serializers.PrimaryKeyRelatedField(queryset=PackageActivity.objects.all(), required=True)
    number_required_files = fields.IntegerField(required=False, default=0)
