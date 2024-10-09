from api.http.serializers.media_thumbnail.media_thumbnail_serializer import MediaThumbnailSerializer
from api.http.serializers.media_thumbnail.project_snapshot_media_thumbnail_list_serializer import \
    ProjectSnapshotMediaThumbnailListSerializer


class ProjectSnapshotMediaThumbnailSerializer(MediaThumbnailSerializer):
    class Meta(MediaThumbnailSerializer.Meta):
        list_serializer_class = ProjectSnapshotMediaThumbnailListSerializer
