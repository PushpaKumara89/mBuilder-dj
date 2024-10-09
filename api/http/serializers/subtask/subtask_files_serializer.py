from rest_framework import serializers

from api.http.serializers import BaseModelSerializer
from api.models import Subtask, Media


class SubtaskFilesSerializer(BaseModelSerializer):
    class Meta:
        model = Subtask
        fields = ('files',)

    files = serializers.PrimaryKeyRelatedField(required=True, queryset=Media.objects.all(), many=True)

    def add(self) -> None:
        files = self.validated_data.pop('files')
        for file in files:
            self.instance.files.add(file)

    def remove(self) -> None:
        files = self.validated_data.pop('files')
        for file in files:
            self.instance.files.remove(file)
