from rest_framework import fields
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

from api.http.serializers.base_model_serializer import BaseModelSerializer

from api.models import User, PackageHandoverDocumentMediaUpdate, PackageHandoverDocument
from api.utilities.status_flow.package_handover_document_media_status_change_flow import \
    PackageHandoverDocumentMediaStatusChangeFlow


class PackageHandoverDocumentMediaUpdateBulkCreateSerializer(BaseModelSerializer):
    class Meta:
        model = PackageHandoverDocumentMediaUpdate
        fields = ('id', 'package_handover_document', 'user', 'comment', 'old_data',
                  'new_data', 'created_at', 'updated_at',)
        expandable_fields = {
            'expanded_user': ('api.http.serializers.UserSerializer', {'source': 'user'})
        }

    package_handover_document = serializers.PrimaryKeyRelatedField(queryset=PackageHandoverDocument.objects.all(), required=True)
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)
    comment = fields.CharField(required=False, allow_null=True)
    old_data = fields.JSONField(required=True)
    new_data = fields.JSONField(required=True)

    def validate(self, attrs):
        status_flow = PackageHandoverDocumentMediaStatusChangeFlow(
            attrs, self.context['request'].user
        )

        if not status_flow.is_valid_bulk_update():
            raise ValidationError(_('This is not a valid status change.'))

        return attrs

