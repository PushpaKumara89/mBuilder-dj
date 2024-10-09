from django.db import models
from rest_framework.serializers import ListSerializer
from typing import Union

from api.models.base_model import BaseModel


class LastEntityListSerializer(ListSerializer):
    def update(self, instance, validated_data):
        pass

    def to_representation(self, data: Union[list, models.Manager]):
        """
        List of object instances -> List of dicts of primitive datatypes.
        """
        # Dealing with nested relationships, data can be a Manager,
        # so, first get a queryset from the Manager if needed
        if hasattr(data.instance, 'last_updates'):
            item = data.instance.last_updates[0] if data.instance.last_updates else {}
        elif isinstance(data, models.Manager):
            item = data.all().order_by('-created_at').first()
        else:
            def sort_callback(entity):
                return getattr(entity, 'created_at') if isinstance(entity, BaseModel) else entity.get('created_at')

            sorted(data, key=sort_callback, reverse=True)

            item = data[0]

        return self.child.to_representation(item) if item else None
