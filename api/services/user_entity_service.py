from typing import Dict
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from rest_framework.request import Request
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from safedelete import HARD_DELETE

from api.models import Recipient, Company, Project, ProjectUser
from api.queues.notify_company_admins_registration_user import notify_company_admins_registration_user
from api.services.base_entity_service import BaseEntityService
from api.queues.send_report import send_csv_report
from api.utilities.tasks_utilities import SerializableRequest


UserModel = get_user_model()


class UserEntityService(BaseEntityService):
    model: UserModel = UserModel

    def logout(self, token: str) -> None:
        try:
            RefreshToken(token).blacklist()
        except TokenError:
            raise InvalidToken

    def delete_own_profile(self, user: UserModel) -> None:
        user.first_name = 'Deleted'
        user.last_name = 'Deleted'
        user.email = None
        user.is_staff = False
        user.is_superuser = False
        user.is_active = False
        user.deleted = now()
        user.phone = None
        user.position = 'Deleted'
        user.save(
            update_fields=['first_name', 'last_name', 'email', 'is_staff', 'is_superuser',
                           'is_active', 'deleted', 'phone', 'position']
        )
        Recipient.objects.filter(user_id=user.id).delete()

    def notify_company_admins_registration_user(self, user_id: int) -> None:
        notify_company_admins_registration_user(user_id)

    def create(self, validated_data: Dict) -> UserModel:
        prepared_validated_data = self._prepare_creation_validated_data(validated_data, status=self.model.Status.APPROVED)

        user = self._make_object_user(prepared_validated_data)
        self._add_group_advantages(user, validated_data['group'].pk)

        user.group = validated_data['group']
        user.save()
        user.groups.set([validated_data['group']])

        return user

    def update(self, instance: UserModel, validated_data: Dict) -> UserModel:
        self._set_password(instance, validated_data)
        self._set_group(instance, validated_data)

        return super().update(instance, validated_data)

    def restore(self, validated_data: Dict) -> None:
        self.model.deleted_objects.filter(**validated_data).get().undelete()

    def register(self, validated_data: Dict) -> UserModel:
        prepared_validated_data = self._prepare_creation_validated_data(validated_data, status=self.model.Status.PENDING)

        user = self._make_object_user(prepared_validated_data)
        self._add_group_advantages(user, self.model.Group.MANAGER)

        user.send_registration_emails = False

        user.group_id = self.model.Group.MANAGER
        user.save()
        user.groups.set([self.model.Group.MANAGER])

        self._assign_user_to_demo_projects(user)

        return user

    def _add_group_advantages(self, user: UserModel, group: int) -> Dict:
        advantage_fields = {'is_superuser': False}
        user.is_superuser = False

        if group == self.model.Group.COMPANY_ADMIN:
            user.is_superuser = True
            user.is_staff = True
            advantage_fields.update({'is_superuser': True, 'is_staff': True})

        if group in [self.model.Group.ADMIN, self.model.Group.MANAGER]:
            user.is_staff = True
            advantage_fields.update({'is_staff': True})

        return advantage_fields

    @staticmethod
    def _assign_user_to_demo_projects(user: UserModel) -> None:
        demo_projects_ids = Project.objects.filter(is_demo=True).values_list('pk', flat=True)
        user.project_set.set(list(demo_projects_ids))

    def _make_object_user(self, validated_data: Dict) -> UserModel:
        user = self.model(**validated_data)
        if 'password' in validated_data:
            user.set_password(validated_data['password'])
        return user

    @staticmethod
    def _exclude_fields_for_creation(data: Dict) -> Dict:
        excluding_fields = ['new_password', 'group', 'status']
        return {field_name: value for field_name, value in data.items() if field_name not in excluding_fields}

    def _prepare_creation_validated_data(self, validated_data: Dict, status: str) -> Dict:
        data = self._exclude_fields_for_creation(validated_data)
        data['status'] = status
        company_name = data.pop('company_name') if 'company_name' in data else None

        if company_name:
            company = Company.all_objects.filter(name__iexact=company_name).first()
            if not company:
                company = Company(name=company_name)
                company.save()

            data['company_id'] = company.pk

        return data

    def _set_password(self, instance: UserModel, validated_data: Dict) -> None:
        if 'password' in validated_data:
            instance.set_password(validated_data['new_password'])
            instance.save()

            del validated_data['password']
            del validated_data['new_password']

    def _set_group(self, instance: UserModel, validated_data: Dict) -> None:
        if 'group' in validated_data:
            group_id = validated_data['group'].pk
            if group_id == UserModel.Group.COMPANY_ADMIN and instance.group_id != group_id:
                self._remove_from_projects(instance)
            validated_data.update(self._add_group_advantages(instance, validated_data['group'].pk))
            instance.groups.set([validated_data['group']])

    @staticmethod
    def _remove_from_projects(instance: UserModel) -> None:
        ProjectUser.objects.filter(user_id=instance.id).delete(force_policy=HARD_DELETE)

    def generate_csv(self, request: Request) -> None:
        serializable_request = SerializableRequest(request)
        send_csv_report(serializable_request, self.model, None, request.user.email)
