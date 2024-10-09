from rest_framework.fields import CharField, ReadOnlyField

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import PackageActivity


class PackageActivityShortSerializer(BaseModelSerializer):

    class Meta:
        fields = ('id', 'name', 'activity_id',)
        model = PackageActivity

    id = ReadOnlyField()
    name = CharField()
    activity_id = CharField()
