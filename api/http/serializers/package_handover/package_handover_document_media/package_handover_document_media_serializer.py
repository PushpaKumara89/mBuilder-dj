from django.db.models import Q
from django.db.models.expressions import RawSQL
from django.utils.translation import gettext as _

from rest_framework import fields
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from api.http.serializers import MediaSerializer, PackageHandoverDocumentSerializer
from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import PackageHandoverDocument, PackageHandoverDocumentMedia, Media
from api.queues.handover_document import create_handover_document_from_package_handover_document_media
from api.services.handover_document_service import HandoverDocumentService


class PackageHandoverDocumentMediaSerializer(BaseModelSerializer):
    class Meta:
        model = PackageHandoverDocumentMedia
        fields = ('id', 'package_handover_document', 'media', 'status', 'last_confirmed_update', 'uid', 'information',)
        expandable_fields = {
            'expanded_package_handover_document': (PackageHandoverDocumentSerializer, {'source': 'package_handover_document'}),
            'expanded_media': (MediaSerializer, {'source': 'media'}),
            'expanded_last_status_change_update': (serializers.SerializerMethodField, {'method_name': 'last_status_change_update'}),
            'expanded_last_confirmed_update': ('api.http.serializers.PackageHandoverDocumentMediaUpdateSerializer', {'source': 'last_confirmed_update'}),
            'expanded_upload_update': (
                'api.http.serializers.package_handover.package_handover_document.package_handover_document_media_upload_update_serializer.PackageHandoverDocumentMediaUploadUpdateSerializer',
                {
                    'many': True,
                    'source': 'packagehandoverdocumentmediaupdate_set'
                }
            ),
        }

    package_handover_document = serializers.PrimaryKeyRelatedField(queryset=PackageHandoverDocument.objects.all(), required=True)
    media = serializers.PrimaryKeyRelatedField(queryset=Media.objects.all(), required=True)
    status = fields.ChoiceField(choices=PackageHandoverDocumentMedia.Status.choices, read_only=True),
    last_confirmed_update = serializers.PrimaryKeyRelatedField(read_only=True)
    uid = serializers.CharField(required=False, allow_null=True, max_length=255, validators=[
        UniqueValidator(queryset=PackageHandoverDocumentMedia.objects.all(),
                        message=_('A document media with this uid already exists.'))
    ])
    information = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    def create(self, validated_data):
        if self.context['request'].user.is_staff:
            validated_data['status'] = PackageHandoverDocumentMedia.Status.REQUESTING_APPROVAL
        else:
            validated_data['status'] = PackageHandoverDocumentMedia.Status.IN_PROGRESS

        package_handover_document_media = super().create(validated_data)

        self.__create_package_handover_document_media_update(package_handover_document_media)
        package_handover_document_media.refresh_from_db()

        if HandoverDocumentService.can_create_from_package_handover_document_media(package_handover_document_media):
            create_handover_document_from_package_handover_document_media(package_handover_document_media)

        return package_handover_document_media

    def last_status_change_update(self, obj: PackageHandoverDocumentMedia):
        from api.http.serializers.package_handover.package_handover_document_media_update.package_handover_document_media_update_serializer import \
            PackageHandoverDocumentMediaUpdateSerializer

        update = self._get_last_status_change_update(obj)

        if update:
            return PackageHandoverDocumentMediaUpdateSerializer(update, context=self.context).data

        return None

    def _get_last_status_change_update(self, obj: PackageHandoverDocumentMedia):
        return obj.packagehandoverdocumentmediaupdate_set. \
            filter(~Q(old_data__status=RawSQL('new_data -> %s', ('status',)))). \
            order_by('-created_at').first()

    def __create_package_handover_document_media_update(self, package_handover_document_media):
        from api.http.serializers.package_handover.package_handover_document_media_update.package_handover_document_media_update_serializer import \
            PackageHandoverDocumentMediaUpdateSerializer

        update_data = {
            'package_handover_document_media': package_handover_document_media.pk,
            'user': self.context['request'].user.pk,
            'old_data': {},
            'new_data': {
                'status': package_handover_document_media.status,
                'media': package_handover_document_media.media.pk
            }
        }

        package_handover_document_media_update_serializer = PackageHandoverDocumentMediaUpdateSerializer(data=update_data, context=self.context)
        package_handover_document_media_update_serializer.is_valid(raise_exception=True)

        return package_handover_document_media_update_serializer.create(
            package_handover_document_media_update_serializer.validated_data
        )
