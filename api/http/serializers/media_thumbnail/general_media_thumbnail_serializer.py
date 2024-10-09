from api.http.serializers.media_thumbnail.general_media_thumbnail_list_serializer import \
    GeneralMediaThumbnailListSerializer
from api.http.serializers.media_thumbnail.media_thumbnail_serializer import MediaThumbnailSerializer


class GeneralMediaThumbnailSerializer(MediaThumbnailSerializer):
    class Meta(MediaThumbnailSerializer.Meta):
        list_serializer_class = GeneralMediaThumbnailListSerializer
