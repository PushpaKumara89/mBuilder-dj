from django.utils.translation import gettext_lazy as _
from rest_framework import fields
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.serializers.media.media_serializer import MediaSerializer
from api.models import Media, PackageHandoverDocumentMedia


class PackageHandoverDocumentMediaUpdateNewDataSerializer(BaseModelSerializer):
    class Meta:
        model = PackageHandoverDocumentMedia
        fields = ('status', 'media', 'uid', 'information',)
        expandable_fields = {
            'expanded_media': (MediaSerializer, {'source': 'media'})
        }

    status = fields.ChoiceField(choices=PackageHandoverDocumentMedia.Status.choices, required=False, allow_blank=False, allow_null=False)
    media = serializers.PrimaryKeyRelatedField(queryset=Media.objects.all(), required=False)
    uid = serializers.CharField(required=False, allow_null=True, validators=[
        UniqueValidator(
            queryset=PackageHandoverDocumentMedia.objects.all(),
            message=_('A document media with this name already exists.'),
            lookup='iexact'
        )
    ])
    information = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    def validate(self, data):
        if hasattr(self, 'initial_data'):
            unknown_keys = set(self.initial_data.keys()) - set(self.fields.keys())

            if unknown_keys:
                raise ValidationError(_('Got unknown fields: {}'.format(unknown_keys)))

            user = self.context.get('user')
            old_data_status = self.context.get('old_data', {}).get('status')
            if (user.is_subcontractor or user.is_consultant) and \
                    old_data_status == PackageHandoverDocumentMedia.Status.CONTESTED.value and \
                    self.initial_data['status'] == PackageHandoverDocumentMedia.Status.IN_PROGRESS.value and \
                    self.initial_data.get('media') is None:
                raise ValidationError(_('Media is required'))

        return data
