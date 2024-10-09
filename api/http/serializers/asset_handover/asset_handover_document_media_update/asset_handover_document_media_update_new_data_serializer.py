from django.utils.translation import gettext_lazy as _
from rest_framework import fields
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator
from rest_framework.validators import UniqueValidator

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.serializers.media.media_serializer import MediaSerializer
from api.models import Media, AssetHandoverDocumentMedia, AssetHandoverDocument


class AssetHandoverDocumentMediaUpdateNewDataSerializer(BaseModelSerializer):
    class Meta:
        model = AssetHandoverDocumentMedia
        fields = ('asset_handover_document', 'status', 'media', 'uid')
        validators = [
            UniqueTogetherValidator(
                fields=['asset_handover_document', 'media'], queryset=AssetHandoverDocumentMedia.objects.all()
            )
        ]
        expandable_fields = {
            'expanded_media': (MediaSerializer, {'source': 'media'})
        }

    asset_handover_document = serializers.PrimaryKeyRelatedField(required=False, queryset=AssetHandoverDocument.objects.all())
    status = fields.ChoiceField(choices=AssetHandoverDocumentMedia.Status.choices, required=True, allow_blank=False, allow_null=False)
    media = serializers.PrimaryKeyRelatedField(required=False, queryset=Media.objects.all())
    uid = serializers.CharField(required=False, allow_null=True, allow_blank=True, validators=[
        UniqueValidator(
            queryset=AssetHandoverDocumentMedia.objects.all(),
            message=_('A document media with this name already exists.'),
            lookup='iexact'
        )
    ])

    def validate(self, data):
        if hasattr(self, 'initial_data'):
            unknown_keys = set(self.initial_data.keys()) - set(self.fields.keys())

            if unknown_keys:
                raise ValidationError(_('Got unknown fields: {}'.format(unknown_keys)))

        return data
