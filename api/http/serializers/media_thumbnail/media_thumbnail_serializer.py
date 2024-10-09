from rest_framework import fields, serializers

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import MediaThumbnail, Media


class MediaThumbnailSerializer(BaseModelSerializer):
    class Meta:
        model = MediaThumbnail
        fields = ('id', 'original_media', 'thumbnail', 'width', 'height',
                  'created_at', 'updated_at')
        expandable_fields = {
            'expanded_original_media': (
                'api.http.serializers.media.media_serializer.MediaSerializer',
                {'source': 'original_media'}
            ),
            'expanded_thumbnail': (
                'api.http.serializers.media.media_serializer.MediaSerializer',
                {'source': 'thumbnail'}
            ),
        }

    original_media = serializers.PrimaryKeyRelatedField(queryset=Media.objects.all())
    thumbnail = serializers.PrimaryKeyRelatedField(queryset=Media.objects.all())
    width = fields.IntegerField(read_only=True)
    height = fields.IntegerField(read_only=True)
