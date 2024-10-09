from django.utils.translation import gettext as _
from rest_framework.fields import EmailField

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.validators import ExistsValidator
from api.models import User


class UserRestoreSerializer(BaseModelSerializer):
    class Meta:
        model = User
        fields = ('email',)

    email = EmailField(required=True, validators=[
        ExistsValidator(queryset=User.deleted_objects.all(), message=_('A user with this email does not exists.'))
    ])
