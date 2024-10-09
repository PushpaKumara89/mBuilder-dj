from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework.fields import CharField, EmailField, ChoiceField

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.models import User


class UserReportSerializer(BaseModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'status', 'first_name', 'last_name', 'email', 'phone', 'position',
            'company', 'group', 'created_at', 'updated_at',
        )
        expandable_fields = {
            'expanded_user_fullname': (serializers.SerializerMethodField, {'method_name': 'user_fullname'}),
            'expanded_user_company_name': (serializers.SerializerMethodField, {'method_name': 'user_company_name'}),
        }

    first_name = CharField(read_only=True)
    status = ChoiceField(choices=User.Status.choices, read_only=True)
    last_name = CharField(read_only=True)
    email = EmailField(read_only=True)
    phone = PhoneNumberField(read_only=True)
    company = serializers.PrimaryKeyRelatedField(read_only=True)
    position = CharField(read_only=True)
    group = serializers.PrimaryKeyRelatedField(read_only=True)

    def user_fullname(self, obj: User):
        return '%s %s' % (obj.first_name, obj.last_name)

    def user_company_name(self, obj: User):
        return obj.company.name
