import json

from rest_framework import serializers


class JSONInStringField(serializers.JSONField):
    def to_representation(self, value):
        return json.loads(value)
