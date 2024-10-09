from django.utils.translation import gettext as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.serializers.package_handover.package_handover_document_media.package_handover_document_media_serializer import PackageHandoverDocumentMediaSerializer
from api.models import Media, Project, PackageHandoverDocumentMedia, Package, PackageActivity, \
    PackageHandoverDocumentType, PackageHandoverDocument
from api.services.media_entity_service import MediaEntityService
from api.utilities.file_utilities import copy_file_by_link


class PackageHandoverDocumentMediaBulkCreateSerializer(BaseModelSerializer):
    class Meta:
        model = PackageHandoverDocumentMedia
        fields = ('project', 'package', 'package_activities', 'media', 'package_handover_document_type',)

    project = serializers.PrimaryKeyRelatedField(required=True, queryset=Project.objects.all())
    package = serializers.PrimaryKeyRelatedField(required=True, queryset=Package.objects.all())
    package_activities = serializers.PrimaryKeyRelatedField(required=True, queryset=PackageActivity.objects.all(), many=True)
    media = serializers.PrimaryKeyRelatedField(queryset=Media.objects.all(), required=True)
    package_handover_document_type = serializers.PrimaryKeyRelatedField(queryset=PackageHandoverDocumentType.objects.all(), required=True)

    def bulk_create(self):
        data = self.validated_data

        package_handover_documents = self.__get_package_handover_documents(data)

        package_handover_document_media_data = self.__get_package_handover_document_media_data(
            package_handover_documents, data['media']
        )

        package_handover_document_media_serializer = PackageHandoverDocumentMediaSerializer(
            data=package_handover_document_media_data,
            context=self.context,
            many=True,
            expand=[
                'expanded_last_confirmed_update',
                'expanded_last_confirmed_update.expanded_user',
                'expanded_last_confirmed_update.expanded_user.expanded_user_company',
                'expanded_last_status_change_update',
                'expanded_media',
                'expanded_upload_update',
                'expanded_upload_update.expanded_user',
                'expanded_upload_update.expanded_user.expanded_user_company'
            ])
        package_handover_document_media_serializer.is_valid(raise_exception=True)
        package_handover_document_media_serializer.save()

        return package_handover_document_media_serializer.data

    def __get_package_handover_documents(self, data):
        return PackageHandoverDocument.objects.filter(
            package_handover__package_matrix__project=data['project'],
            package_handover__package_matrix__package_activity__in=data['package_activities'],
            package_handover__package_matrix__package=data['package'],
            package_handover_document_type=data['package_handover_document_type']
        ).all()

    def __get_package_handover_document_media_data(self, package_handover_documents, media):
        package_handover_document_media_data = []

        for package_handover_document in package_handover_documents:
            copied_file = copy_file_by_link(media.original_link, media.name, media.is_public)
            copied_media = MediaEntityService().create({'file': copied_file, 'is_public': False})

            package_handover_document_media_data.append({
                'package_handover_document': package_handover_document.pk,
                'media': copied_media.pk
            })

        return package_handover_document_media_data

    def validate(self, attrs):
        if self.context['request'].user.is_subcontractor:
            def does_subcontractor_not_from_whitelisted_company():
                return not PackageHandoverDocument.objects.filter(
                    package_handover__package_matrix__project=attrs['project'],
                    package_handover__package_matrix__package_activity__in=attrs['package_activities'],
                    package_handover__package_matrix__package=attrs['package'],
                    package_handover__package_matrix__packagematrixcompany__company_id=self.context['request'].user.company.pk,
                    package_handover_document_type=attrs['package_handover_document_type']
                ).exists()

            if does_subcontractor_not_from_whitelisted_company():
                raise ValidationError(_('You\'re not allowed to create media.'))

        return attrs
