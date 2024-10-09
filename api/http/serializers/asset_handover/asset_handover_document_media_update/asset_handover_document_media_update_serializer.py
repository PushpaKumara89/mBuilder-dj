from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from api.http.serializers.asset_handover.asset_handover_document_media_update.asset_handover_document_media_update_new_data_serializer import \
    AssetHandoverDocumentMediaUpdateNewDataSerializer
from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import AssetHandoverDocumentMedia, User
from api.models.asset_handover import AssetHandoverDocumentMediaUpdate
from api.queues.handover_document import create_handover_document_on_asset_handover_document_media_update, \
    update_handover_document_on_asset_handover_document_media_update, remove_handover_document_on_asset_handover_document_media_update
from api.services.handover_document_service import HandoverDocumentService
from api.utilities.status_flow.asset_handover_document_media_status_change_flow import AssetHandoverDocumentMediaStatusChangeFlow
from api.utilities.status_flow.update_flow_utilities import set_last_confirmed_update


class AssetHandoverDocumentMediaUpdateSerializer(BaseModelSerializer):
    class Meta:
        model = AssetHandoverDocumentMediaUpdate
        fields = ('id', 'asset_handover_document_media', 'user', 'comment', 'old_data', 'new_data',
                  'created_at', 'updated_at', 'company')
        expandable_fields = {
            'expanded_asset_handover_document_media': ('api.http.serializers.AssetHandoverDocumentMediaSerializer',
                                                       {'source': 'asset_handover_document_media'}),
            'expanded_user': ('api.http.serializers.UserSerializer', {'source': 'user'}),
            'expanded_company': ('api.http.serializers.CompanySerializer', {'source': 'company'})
        }

    asset_handover_document_media = serializers.PrimaryKeyRelatedField(
        required=True, queryset=AssetHandoverDocumentMedia.objects.all())
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)
    company = serializers.PrimaryKeyRelatedField(read_only=True)
    comment = serializers.CharField(required=False, allow_null=True)
    old_data = serializers.JSONField(required=True)
    new_data = serializers.JSONField(required=False)

    def create(self, validated_data):
        from api.http.serializers import AssetHandoverDocumentMediaSerializer
        from api.queues.asset_handover_statistics import change_statistics_on_asset_handover_document_media_update_create

        media_update_new_data_serializer = AssetHandoverDocumentMediaUpdateNewDataSerializer(
            validated_data['asset_handover_document_media'], data=validated_data['new_data'], context=self.context)
        media_update_new_data_serializer.is_valid(raise_exception=True)

        asset_handover_document_media_serializer = AssetHandoverDocumentMediaSerializer()
        asset_handover_document_media_serializer.update(media_update_new_data_serializer.instance,
                                                        media_update_new_data_serializer.validated_data)

        validated_data['company'] = self.context['request'].user.company
        asset_handover_document_media_update = super().create(validated_data)
        set_last_confirmed_update(asset_handover_document_media_update, self.context['request'].user)
        asset_handover_document_media_update.refresh_from_db()

        change_statistics_on_asset_handover_document_media_update_create(asset_handover_document_media_update, self.context['request'].user)

        if HandoverDocumentService.need_to_create_from_asset_handover_document_media(asset_handover_document_media_update):
            create_handover_document_on_asset_handover_document_media_update(asset_handover_document_media_update)

        if HandoverDocumentService.need_to_remove_asset_handover_document_media(asset_handover_document_media_update):
            remove_handover_document_on_asset_handover_document_media_update(asset_handover_document_media_update)

        if any(field in validated_data['new_data'] for field in ['uid', 'media']):
            update_handover_document_on_asset_handover_document_media_update(asset_handover_document_media_update)

        return asset_handover_document_media_update

    def validate(self, data):
        user = self.context['request'].user
        new_data = data.get('new_data', {})
        old_data = data.get('old_data', {})
        status_flow = AssetHandoverDocumentMediaStatusChangeFlow(data, user)

        if not status_flow.is_valid_change():
            raise ValidationError({'status': _('You cannot change status from %s to %s.' % (old_data.get('status'),
                                                                                            new_data.get('status'),))})

        return data
