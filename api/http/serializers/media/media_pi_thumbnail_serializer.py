from rest_framework import fields

from api.http.serializers import MediaSerializer
from api.models import Media


class MediaPinThumbnailSerializer(MediaSerializer):
    class Meta(MediaSerializer.Meta):
        model = Media
        fields = MediaSerializer.Meta.fields + ('type',)

    type = fields.CharField(read_only=True)
