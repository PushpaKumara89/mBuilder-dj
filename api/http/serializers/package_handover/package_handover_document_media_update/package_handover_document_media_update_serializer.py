from rest_framework import fields
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.serializers.package_handover.package_handover_document_media.package_handover_document_media_serializer import \
    PackageHandoverDocumentMediaSerializer
from api.http.serializers.package_handover.package_handover_document_media_update.package_handover_document_media_update_new_data_serializer import \
            PackageHandoverDocumentMediaUpdateNewDataSerializer

from api.models import User, PackageHandoverDocumentMedia, PackageHandoverDocumentMediaUpdate, Company
from api.queues.handover_document import create_handover_document_on_package_handover_document_media_update, update_handover_document_on_package_handover_document_media_update, \
    remove_handover_document_on_package_handover_document_media_update
from api.queues.package_handover_statistics import change_statistics_on_package_handover_document_media_update_create
from api.services.handover_document_service import HandoverDocumentService
from api.utilities.status_flow.package_handover_document_media_status_change_flow import \
    PackageHandoverDocumentMediaStatusChangeFlow
from api.utilities.status_flow.update_flow_utilities import set_last_confirmed_update


class PackageHandoverDocumentMediaUpdateSerializer(BaseModelSerializer):
    class Meta:
        model = PackageHandoverDocumentMediaUpdate
        fields = ('id', 'package_handover_document_media', 'user', 'comment', 'old_data',
                  'new_data', 'created_at', 'updated_at', 'company')
        expandable_fields = {
            'expanded_user': ('api.http.serializers.UserSerializer', {'source': 'user'}),
            'expanded_company': ('api.http.serializers.CompanySerializer', {'source': 'company'})
        }

    package_handover_document_media = serializers.PrimaryKeyRelatedField(queryset=PackageHandoverDocumentMedia.objects.all(), required=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)
    company = serializers.PrimaryKeyRelatedField(read_only=True)
    comment = fields.CharField(required=False, allow_null=True)
    old_data = fields.JSONField(required=True)
    new_data = fields.JSONField(required=True)

    def create(self, validated_data):
        package_handover_document_media_pk = validated_data['package_handover_document_media']

        document_media_update_new_data_serializer = PackageHandoverDocumentMediaUpdateNewDataSerializer(
            package_handover_document_media_pk,
            data=validated_data['new_data'],
            context={'user': validated_data['user'], 'old_data': validated_data['old_data']}
        )
        document_media_update_new_data_serializer.is_valid(raise_exception=True)

        document_media_serializer = PackageHandoverDocumentMediaSerializer()
        document_media_serializer.update(document_media_update_new_data_serializer.instance,
                                         document_media_update_new_data_serializer.validated_data)
        validated_data['company'] = self.context['request'].user.company
        package_handover_document_media_update = super().create(validated_data)

        set_last_confirmed_update(package_handover_document_media_update, self.context['request'].user)
        package_handover_document_media_update.refresh_from_db()

        change_statistics_on_package_handover_document_media_update_create(package_handover_document_media_update, self.context['request'].user)

        if HandoverDocumentService.need_to_create_from_package_handover_document_media(package_handover_document_media_update):
            create_handover_document_on_package_handover_document_media_update(package_handover_document_media_update)

        if HandoverDocumentService.need_to_remove_package_handover_document_media(package_handover_document_media_update):
            remove_handover_document_on_package_handover_document_media_update(package_handover_document_media_update)

        if any(field in validated_data['new_data'] for field in ['uid', 'information', 'media']):
            update_handover_document_on_package_handover_document_media_update(package_handover_document_media_update)

        return package_handover_document_media_update

    def to_representation(self, instance):
        data = super().to_representation(instance)

        request = self.context.get('request')
        if request and request.user.is_client and not self.__is_available_for_client(data):
            del data['comment']

        return data

    def validate(self, data):
        user = self.context['request'].user
        new_data = data.get('new_data', {})
        old_data = data.get('old_data', {})
        status_flow = PackageHandoverDocumentMediaStatusChangeFlow(data, user)

        if not status_flow.is_valid_change():
            raise ValidationError({'status': _('You cannot change status from %s to %s.' % (old_data.get('status'),
                                                                                            new_data.get('status'),))})

        return data

    def __is_available_for_client(self, data: dict) -> bool:
        old_status = data.get('old_data', {}).get('status')
        new_status = data.get('new_data', {}).get('status')

        return not (
            (old_status == PackageHandoverDocumentMedia.Status.IN_PROGRESS and new_status == PackageHandoverDocumentMedia.Status.CONTESTED) or
            (old_status == PackageHandoverDocumentMedia.Status.CONTESTED and new_status == PackageHandoverDocumentMedia.Status.IN_PROGRESS)
        )
