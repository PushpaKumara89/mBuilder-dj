from rest_framework import fields, serializers
from rest_framework.validators import UniqueTogetherValidator

from api.http.serializers import BaseModelSerializer, LocationMatrixSerializer, PackageMatrixSerializer, \
    PackageSerializer
from api.http.serializers.location_matrix_package.location_matrix_package_list_serializer import \
    LocationMatrixPackageListSerializer
from api.http.serializers.media.media_serializer import MediaSerializer
from api.models import LocationMatrix, LocationMatrixPackage, PackageMatrix


class LocationMatrixPackagesSerializer(BaseModelSerializer):
    class Meta:
        model = LocationMatrixPackage
        fields = ('id', 'location_matrix', 'package_matrix', 'enabled', 'media', 'package', 'package_activity',
                  'package_activity_name', 'created_at', 'updated_at',)
        list_serializer_class = LocationMatrixPackageListSerializer
        validators = [
            UniqueTogetherValidator(
                fields=['location_matrix', 'package_matrix'],
                queryset=LocationMatrixPackage.objects.all()
            )
        ]
        expandable_fields = {
            'expanded_location_matrix': (LocationMatrixSerializer, {'source': 'location_matrix'}),
            'expanded_package_matrix': (PackageMatrixSerializer, {'source': 'package_matrix'}),
            'expanded_media': (MediaSerializer, {'many': True, 'source': 'media'}),
            'expanded_package': (PackageSerializer, {'source': 'package'}),
            'expanded_media_count': (serializers.SerializerMethodField, {'method_name': 'media_count'})
        }

    location_matrix = serializers.PrimaryKeyRelatedField(queryset=LocationMatrix.objects.all(), required=True)
    package_matrix = serializers.PrimaryKeyRelatedField(queryset=PackageMatrix.objects.all(), required=True)
    enabled = fields.BooleanField(required=False)
    media = MediaSerializer(source='files_set', many=True, required=False, read_only=True)

    package = serializers.PrimaryKeyRelatedField(read_only=True)
    package_activity = serializers.PrimaryKeyRelatedField(read_only=True)
    package_activity_name = fields.CharField(read_only=True)

    def create(self, validated_data):
        self.__set_data_from_package_matrix(validated_data)

        return self.Meta.model.objects.create(**validated_data)

    def update(self, instance: LocationMatrixPackage, validated_data):
        if validated_data['package_matrix'] is not None and instance.package_matrix.pk != validated_data['package_matrix'].pk:
            self.__set_data_from_package_matrix(validated_data)

        return super().update(instance, validated_data)

    def media_count(self, obj):
        return int(obj.media_count) if getattr(obj, 'media_count') else 0

    def __set_data_from_package_matrix(self, validated_data):
        validated_data['package'] = validated_data['package_matrix'].package
        validated_data['package_activity'] = validated_data['package_matrix'].package_activity
        validated_data['package_activity_name'] = validated_data['package_matrix'].package_activity.name
