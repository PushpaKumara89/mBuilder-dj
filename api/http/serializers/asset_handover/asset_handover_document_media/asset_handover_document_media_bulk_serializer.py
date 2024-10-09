from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.serializers.asset_handover.asset_handover_document_media.asset_handover_document_media_serializer import \
    AssetHandoverDocumentMediaSerializer
from api.http.serializers.asset_handover.asset_handover_document_media.asset_handover_document_media_bulk_item_serializer import \
    AssetHandoverDocumentMediaBulkItemSerializer

from api.models import AssetHandoverDocument, AssetHandoverDocumentMedia, Media, AssetHandoverDocumentType, \
    PackageMatrixCompany
from api.services.media_entity_service import MediaEntityService
from api.utilities.file_utilities import copy_file_by_link


class AssetHandoverDocumentMediaBulkSerializer(BaseModelSerializer):
    class Meta:
        model = AssetHandoverDocumentMedia
        fields = ('id', 'document_type', 'bulk_items',
                  'media', 'created_at', 'updated_at',)

    bulk_items = AssetHandoverDocumentMediaBulkItemSerializer(many=True, write_only=True)
    media = serializers.PrimaryKeyRelatedField(required=True, queryset=Media.objects.all(), many=True)
    document_type = serializers.PrimaryKeyRelatedField(required=True, queryset=AssetHandoverDocumentType.objects.all())

    def create(self, validated_data):
        asset_handover_documents = self.__get_asset_handover_documents()
        document_media = self.__get_asset_handover_document_media_data(asset_handover_documents, validated_data['media'])
        serializer = AssetHandoverDocumentMediaSerializer(many=True, context=self.context, data=document_media)
        serializer.is_valid(raise_exception=True)

        created_media = serializer.create(serializer.validated_data)
        return AssetHandoverDocumentMediaSerializer(created_media, many=True, expand=[
            'expanded_last_confirmed_update',
            'expanded_last_confirmed_update.expanded_user',
            'expanded_last_confirmed_update.expanded_user.expanded_user_company',
            'expanded_last_status_change_update',
            'expanded_media',
            'expanded_upload_update',
            'expanded_upload_update.expanded_user',
            'expanded_upload_update.expanded_user.expanded_user_company'
        ]).data

    def validate(self, attrs):
        if self.context['request'].user.is_subcontractor and not self.__is_subcontractor_allowed_to_use_requested_package_matrices(attrs):
            raise ValidationError(_('You\'re not allowed to create media.'))

        return attrs

    def __is_subcontractor_allowed_to_use_requested_package_matrices(self, attrs: dict):
        package_activities_ids = []
        packages_ids = []
        for bulk_item in attrs['bulk_items']:
            packages_ids.append(bulk_item['package'].id)
            package_activities_ids.append(bulk_item['package_activity'].id)

        needed_subcontractor_companies_count = len(package_activities_ids)
        actual_subcontractor_companies_count = PackageMatrixCompany.objects.filter(
            package_matrix__package_activity_id__in=package_activities_ids,
            package_matrix__project_id=self.context['view'].kwargs['project_pk'],
            company_id=self.context['request'].user.company_id
        ).count()

        return needed_subcontractor_companies_count == actual_subcontractor_companies_count

    def __get_asset_handover_documents(self):
        conditions = None
        for bulk_item in self.validated_data['bulk_items']:
            condition = Q(
                asset_handover__package_activity=bulk_item['package_activity'],
                asset_handover__location_matrix__locationmatrixpackage__package=bulk_item['package'],
                asset_handover__location_matrix__locationmatrixpackage__package_activity=bulk_item['package_activity'],
                asset_handover__location_matrix=bulk_item['location_matrix'],
            )
            if conditions is None:
                conditions = condition
            else:
                conditions |= condition

        return list(
            AssetHandoverDocument.objects.filter(
                conditions,
                asset_handover__location_matrix__locationmatrixpackage__enabled=True,
                asset_handover__location_matrix__project_id=self.context['view'].kwargs['project_pk'],
                document_type_id=self.validated_data['document_type'].pk
            ).distinct().all()
        )

    def __get_asset_handover_document_media_data(self, asset_handover_documents, files):
        asset_handover_document_media_data = []

        for asset_handover_document in asset_handover_documents:
            for media in files:
                copied_file = copy_file_by_link(media.original_link, media.name, media.is_public)

                copied_media = MediaEntityService().create({'file': copied_file, 'is_public': False})

                asset_handover_document_media_data.append({
                    'asset_handover_document': asset_handover_document.pk,
                    'media': copied_media.pk
                })

        return asset_handover_document_media_data
