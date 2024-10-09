from django.db.models import Q
from django.db.models.expressions import RawSQL
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from rest_framework.validators import UniqueTogetherValidator

from api.http.serializers.asset_handover import AssetHandoverDocumentSerializer
from api.http.serializers.base_model_serializer import BaseModelSerializer
from rest_framework.validators import UniqueValidator
from api.models import AssetHandoverDocument, AssetHandoverDocumentMedia, Media
from api.queues.handover_document import create_handover_document_from_asset_handover_document_media
from api.services.handover_document_service import HandoverDocumentService


class AssetHandoverDocumentMediaSerializer(BaseModelSerializer):
    class Meta:
        model = AssetHandoverDocumentMedia
        fields = ('id', 'asset_handover_document', 'last_confirmed_update',
                  'media', 'uid', 'status', 'created_at', 'updated_at',)
        validators = [
            UniqueTogetherValidator(
                fields=['asset_handover_document', 'media'], queryset=AssetHandoverDocumentMedia.objects.all()
            )
        ]
        expandable_fields = {
            'expanded_asset_handover_document': (AssetHandoverDocumentSerializer, {'source': 'asset_handover_document'}),
            'expanded_last_status_change_update': (serializers.SerializerMethodField, {'method_name': 'last_status_change_update'}),
            'expanded_media': ('api.http.serializers.MediaSerializer', {'source': 'media'}),
            'expanded_last_confirmed_update': ('api.http.serializers.AssetHandoverDocumentMediaUpdateSerializer',
                                               {'source': 'last_confirmed_update'}),
            'expanded_upload_update': (
                                          'api.http.serializers.asset_handover.asset_handover_document.asset_handover_document_media_upload_update_serializer.AssetHandoverDocumentMediaUploadUpdateSerializer',
                                          {
                                              'many': True,
                                              'source': 'assethandoverdocumentmediaupdate_set'
                                          }
                                      ),
        }

    asset_handover_document = serializers.PrimaryKeyRelatedField(required=True, queryset=AssetHandoverDocument.objects.all())
    media = serializers.PrimaryKeyRelatedField(required=True, queryset=Media.objects.all())
    uid = serializers.CharField(required=False, allow_null=True, max_length=255, validators=[
        UniqueValidator(queryset=AssetHandoverDocumentMedia.objects.all(),
                        message=_('A document media with this uid already exists.'))
    ])
    status = serializers.ChoiceField(required=False, choices=AssetHandoverDocumentMedia.Status.choices)
    last_confirmed_update = serializers.PrimaryKeyRelatedField(read_only=True)

    def create(self, validated_data):
        from api.http.serializers import AssetHandoverDocumentMediaUpdateSerializer

        validated_data['status'] = AssetHandoverDocumentMedia.Status.IN_PROGRESS \
            if self.context['request'].user.is_subcontractor \
            else AssetHandoverDocumentMedia.Status.REQUESTING_APPROVAL

        asset_handover_document_media = super().create(validated_data)
        asset_handover_document_media_update_data = self.__prepare_asset_handover_document_media_update_data(
            asset_handover_document_media
        )

        asset_handover_document_media_update_serializer = AssetHandoverDocumentMediaUpdateSerializer(
            data=asset_handover_document_media_update_data, context=self.context)
        asset_handover_document_media_update_serializer.is_valid(raise_exception=True)
        asset_handover_document_media_update_serializer.create(
            asset_handover_document_media_update_serializer.validated_data
        )

        if HandoverDocumentService.can_create_from_asset_handover_document_media(asset_handover_document_media):
            create_handover_document_from_asset_handover_document_media(asset_handover_document_media)

        return asset_handover_document_media

    def __prepare_asset_handover_document_media_update_data(self, asset_handover_document_media):
        return {
            'comment': None,
            'asset_handover_document_media': asset_handover_document_media.pk,
            'user': self.context['request'].user.pk,
            'old_data': {},
            'new_data': {
                'media': asset_handover_document_media.media.pk,
                'status': asset_handover_document_media.status
            }
        }

    def last_status_change_update(self, obj: AssetHandoverDocumentMedia):
        from api.http.serializers.asset_handover.asset_handover_document_media_update.asset_handover_document_media_update_serializer import \
            AssetHandoverDocumentMediaUpdateSerializer

        update = self._get_last_status_change_update(obj)

        if update:
            return AssetHandoverDocumentMediaUpdateSerializer(update, context=self.context).data

        return None

    def _get_last_status_change_update(self, obj: AssetHandoverDocumentMedia):
        return obj.assethandoverdocumentmediaupdate_set. \
            filter(~Q(old_data__status=RawSQL('new_data -> %s', ('status',)))). \
            order_by('-created_at').first()
