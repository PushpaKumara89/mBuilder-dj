from abc import abstractmethod, ABC
from typing import Union

from django.db import models
from django.forms import model_to_dict
from rest_framework.serializers import ListSerializer

from api.http.serializers import BaseModelSerializer
from api.models.base_model import BaseModel


class StatisticsAggregationListSerializer(ListSerializer, ABC):
    aggregation_fields_serializer_class: BaseModelSerializer

    def to_representation(self, data: Union[list, models.Manager]):
        fields = self.aggregation_fields_serializer_class.Meta.fields
        aggregation = {field: 0 for field in fields}
        if isinstance(data, models.Manager):
            data = list(data.all())

        for entity in data:
            if isinstance(entity, BaseModel):
                entity = model_to_dict(entity)
            for agg_field, agg_value in aggregation.items():
                if self._skip_field(agg_field):
                    continue
                aggregation[agg_field] = agg_value + entity.get(agg_field, 0)

        return self.aggregation_fields_serializer_class(aggregation).data

    @abstractmethod
    def _skip_field(self, field_name: str) -> bool:
        pass