from django.db.models import Q
from django.db.models.manager import Manager
from rest_framework.serializers import ListSerializer

from api.models import MediaThumbnail


class ProjectSnapshotMediaThumbnailListSerializer(ListSerializer):
    def to_representation(self, data: Manager):
        conditions = Q()
        for sizes in MediaThumbnail.PROJECT_SNAPSHOT_THUMBNAIL_SIZES:
            conditions |= Q(width=sizes.width, height=sizes.height)

        return [self.child.to_representation(item) for item in data.filter(conditions).all()]
