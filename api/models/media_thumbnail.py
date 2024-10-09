import dataclasses

from django.db import models
from safedelete import SOFT_DELETE

from api.models.base_model import BaseModel


@dataclasses.dataclass
class ThumbnailSizes:
    width: int
    height: int


class MediaThumbnail(BaseModel):
    _safedelete_policy = SOFT_DELETE

    class Meta(BaseModel.Meta):
        db_table = 'media_thumbnails'

    PROJECT_SNAPSHOT_THUMBNAIL_SIZES = [
        ThumbnailSizes(width=72, height=72)
    ]

    PROJECT_IMAGE_THUMBNAIL_SIZES = [
        ThumbnailSizes(width=32, height=32),
        ThumbnailSizes(width=64, height=64),
        ThumbnailSizes(width=78, height=78),
        ThumbnailSizes(width=88, height=88),
        ThumbnailSizes(width=156, height=156),
        ThumbnailSizes(width=176, height=176),
        ThumbnailSizes(width=540, height=540),
        ThumbnailSizes(width=1080, height=1080)
    ]

    PDF_THUMBNAIL_DPI_SIZES = ThumbnailSizes(width=150, height=150)

    original_media = models.ForeignKey('Media', on_delete=models.CASCADE)
    thumbnail = models.ForeignKey('Media', on_delete=models.CASCADE, related_name='media_thumbnail')
    width = models.IntegerField(null=True)
    height = models.IntegerField(null=True)