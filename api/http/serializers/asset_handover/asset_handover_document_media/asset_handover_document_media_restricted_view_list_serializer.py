from django.db import models
from rest_framework.serializers import ListSerializer
from typing import Union

from api.models import AssetHandoverDocumentMedia


class AssetHandoverDocumentMediaRestrictedViewListSerializer(ListSerializer):
    def update(self, instance, validated_data):
        pass

    def to_representation(self, data: Union[list, models.Manager]):
        """
        List of object instances -> List of dicts of primitive datatypes.
        """
        if isinstance(data, models.Manager):
            if self.child.context['request'].user.is_consultant:
                items = data.filter(status=AssetHandoverDocumentMedia.Status.ACCEPTED)
            elif self.child.context['request'].user.is_client:
                items = data.filter(status__in=[AssetHandoverDocumentMedia.Status.REQUESTING_APPROVAL,
                                                AssetHandoverDocumentMedia.Status.REQUESTED_APPROVAL_REJECTED,
                                                AssetHandoverDocumentMedia.Status.ACCEPTED])
            else:
                items = data.all()
        else:
            if self.child.context['request'].user.is_consultant:
                items = list(
                    filter(
                        lambda media: media.status == AssetHandoverDocumentMedia.Status.ACCEPTED,
                        data
                    )
                )
            elif self.child.context['request'].user.is_client:
                items = list(
                    filter(
                        lambda media: media.status in [
                            AssetHandoverDocumentMedia.Status.REQUESTING_APPROVAL,
                            AssetHandoverDocumentMedia.Status.REQUESTED_APPROVAL_REJECTED,
                            AssetHandoverDocumentMedia.Status.ACCEPTED
                        ],
                        data
                    )
                )
            else:
                items = data

        if items is None:
            items = []

        return [self.child.to_representation(item) for item in items]
