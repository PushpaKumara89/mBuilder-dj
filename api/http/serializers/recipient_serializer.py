from rest_framework import fields, serializers

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.serializers.user.user_serializer import UserSerializer
from api.models import Recipient, User


class RecipientSerializer(BaseModelSerializer):
    class Meta:
        model = Recipient
        fields = (
            'id', 'first_name', 'last_name', 'email', 'user', 'created_at', 'updated_at',
        )
        expandable_fields = {
            'expanded_user': (UserSerializer, {'source': 'user'})
        }

    id = fields.IntegerField(required=False, allow_null=True)
    first_name = fields.CharField(required=False, max_length=255, allow_blank=True)
    last_name = fields.CharField(required=False, max_length=255, allow_blank=True)
    email = fields.EmailField(required=True, max_length=255)
    user = serializers.PrimaryKeyRelatedField(required=False, allow_null=True, queryset=User.objects.all())
