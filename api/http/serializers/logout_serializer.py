from rest_framework import serializers


class LogoutSerializer(serializers.Serializer):
    token = ''
    refresh = serializers.CharField()

    def validate(self, attrs):
        self.token = attrs['refresh']
        return super().validate(attrs)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
