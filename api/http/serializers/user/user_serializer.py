from typing import Dict

from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext as _
from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers
from rest_framework.fields import CharField, EmailField, SerializerMethodField, ChoiceField, DateTimeField
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import PasswordField

from api.exceptions.user_existed_before import UserExistedBefore
from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.serializers.user_project_serializer import UserProjectSerializer
from api.models import User, Company
from api.http.serializers.company_serializer import CompanySerializer


class UserSerializer(BaseModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'status', 'first_name', 'last_name', 'email', 'phone', 'position', 'company_name', 'new_password',
            'company', 'password', 'group', 'created_at', 'updated_at', 'is_api_access_allowed'
        )
        expandable_fields = {
            'expanded_projects': (UserProjectSerializer, {'many': True, 'source': 'project_set'}),
            'expanded_is_notifications_enabled': (SerializerMethodField, {'method_name': 'is_notifications_enabled'}),
            'expanded_user_company': (CompanySerializer, {'source': 'company'}),
            'expanded_deleted': (DateTimeField, {'source': 'deleted'})
        }

    first_name = CharField(required=True)
    status = ChoiceField(choices=User.Status.choices, read_only=True)
    last_name = CharField(required=True)
    email = EmailField(required=True, validators=[
        UniqueValidator(queryset=User.objects.all(),
                        message=_('A user with this email already exists.'),
                        lookup='iexact')
    ])
    phone = PhoneNumberField(required=True)
    company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all(), required=False, allow_null=True, default=None)
    company_name = serializers.CharField(required=False, write_only=True)
    position = CharField(required=True)
    password = PasswordField(required=False)
    new_password = CharField(required=False)
    group = serializers.PrimaryKeyRelatedField(required=True, queryset=Group.objects.all())
    is_api_access_allowed = serializers.BooleanField(required=False)

    default_error_messages = {
        'new_password_not_exists': _('Please fill previous password'),
        'invalid_old_password': _('Not valid password'),
        'password_not_exists': _('Please fill previous password')
    }

    def is_notifications_enabled(self, obj: User):
        if hasattr(obj, 'is_notifications_enabled'):
            return obj.is_notifications_enabled
        return False

    @staticmethod
    def validate_email(email: str) -> str:
        if User.deleted_objects.filter(email=email).exists():
            raise UserExistedBefore(email=email)
        return email

    def validate(self, data: Dict) -> Dict:
        def valid_user_password(password: str) -> bool:
            return self.instance.check_password(password)

        if 'method' in self.context and self.context['method'] == 'PUT':
            if ('new_password' in data) and ('password' not in data):
                self.non_field_fail('password', 'password_not_exists')

            if ('password' in data) and ('new_password' not in data):
                self.non_field_fail('new_password', 'new_password_not_exists')

            if ('password' in data) and not valid_user_password(data['password']):
                self.non_field_fail('password', 'invalid_old_password')

            if ('password' in data) and ('new_password' in data):
                validate_password(data['new_password'], self.instance)

        return data
