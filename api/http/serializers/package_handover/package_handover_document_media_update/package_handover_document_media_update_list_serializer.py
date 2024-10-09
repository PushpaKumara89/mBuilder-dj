from django.db import models
from rest_framework.serializers import ListSerializer
from typing import Union

from api.models.base_model import BaseModel


class PackageHandoverDocumentMediaUpdateListSerializer(ListSerializer):
    def update(self, instance, validated_data):
        pass

    def to_representation(self, data: Union[list, models.Manager]):
        """
        List of object instances -> List of dicts of primitive datatypes.
        """
        # Dealing with nested relationships, data can be a Manager,
        # so, first get a queryset from the Manager if needed
        if isinstance(data, models.Manager):
            # Get the last update when document media was uploaded.
            item = data.filter(new_data__media__isnull=False).order_by('-created_at').first()
        else:
            def sort_callback(entity):
                return getattr(entity, 'created_at') if isinstance(entity, BaseModel) else entity.get('created_at')

            sorted(data, key=sort_callback, reverse=True)
            item = None
            for doc_media_update in data:
                if isinstance(doc_media_update, BaseModel):
                    item = doc_media_update if getattr(doc_media_update, 'new_data').get('media') else None
                    break
                elif doc_media_update['new_data'].get('media'):
                    item = doc_media_update
                    break

        return self.child.to_representation(item) if item else None
