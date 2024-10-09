from rest_framework import serializers

from api.http.serializers import BaseModelSerializer
from api.models import LocationMatrixPackage, Media


class LocationMatrixPackagesMediaSerializer(BaseModelSerializer):
    class Meta:
        model = LocationMatrixPackage
        fields = ('media',)

    media = serializers.PrimaryKeyRelatedField(required=True, queryset=Media.objects.all(), many=True)

    def add(self) -> None:
        files = self.validated_data.pop('media')
        for file in files:
            self.instance.media.add(file)

    def remove(self) -> None:
        files = self.validated_data.pop('media')
        for file in files:
            self.instance.media.remove(file)
