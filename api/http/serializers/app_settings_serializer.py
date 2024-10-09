from rest_framework import serializers


class AppSettingsSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    disable_user_registration_from_mobile_devices = serializers.BooleanField()
