from rest_framework import fields, serializers

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.serializers.fields.media_file_url_serializer import MediaFileUrl
from api.models import Media


class MediaSerializer(BaseModelSerializer):
    class Meta:
        model = Media
        fields = ('id', 'name', 'link', 'file', 'size', 'hash', 'is_public', 'created_at',
                  'updated_at', 'local_id', 'extension', 'sync_create_thumbnails')
        expandable_fields = {
            'expanded_project_snapshot_thumbnails': (
                'api.http.serializers.media_thumbnail.project_snapshot_media_thumbnail_serializer.ProjectSnapshotMediaThumbnailSerializer',
                {'source': 'mediathumbnail_set', 'many': True}
            ),
            'expanded_thumbnails': (
                'api.http.serializers.media_thumbnail.general_media_thumbnail_serializer.GeneralMediaThumbnailSerializer',
                {'source': 'mediathumbnail_set', 'many': True}
            ),
            'expanded_extension': (serializers.SerializerMethodField, {'method_name': 'get_file_extension'})
        }

    file = fields.FileField(write_only=True)
    name = fields.CharField(max_length=255, required=False)
    link = MediaFileUrl(max_length=255, required=False)
    size = fields.IntegerField(read_only=True)
    is_public = fields.BooleanField(required=False, default=True)
    hash = fields.CharField(read_only=True)
    local_id = fields.CharField(required=False, allow_null=True, max_length=255)
    extension = fields.CharField(read_only=True)
    sync_create_thumbnails = fields.BooleanField(write_only=True, required=False)

    def get_file_extension(self, obj: Media):
        return obj.extension
