import pendulum
from typing import Dict

from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request

from api.models import Project
from api.services.asset_register_entity_service import AssetRegisterEntityService
from api.services.base_entity_service import BaseEntityService
from api.queues.media import generate_project_image_thumbnails
from api.queues.destroy_project import cascade_delete_project_with_related_entities
from api.queues.update_project_subtasks_defect_status import update_project_subtasks_defect_status
from api.queues.send_report import send_csv_report
from api.utilities.tasks_utilities import SerializableRequest


class ProjectEntityService(BaseEntityService):
    model = Project

    def update_project(self, project: Project, validated_data: Dict) -> Project:
        if 'image_id' in validated_data:
            validated_data['image'] = validated_data.pop('image_id')

            current_image_pk = getattr(project, 'image_id')
            if validated_data['image'] is not None and validated_data['image'].pk is not current_image_pk:
                generate_project_image_thumbnails(validated_data['image'].link)

        project = self.update(project, validated_data)

        if 'completion_date' in validated_data:
            update_project_subtasks_defect_status(project.pk, str(project.completion_date))

        return project

    def create_project(self, validated_data: Dict) -> Project:
        if 'image_id' in validated_data:
            validated_data['image'] = validated_data.pop('image_id')

            if validated_data['image'] is not None:
                generate_project_image_thumbnails(validated_data['image'].link)

        project = self.create(validated_data)

        AssetRegisterEntityService().create({
            'data': {},
            'project_id': project.id
        })

        return project

    def destroy_project(self, project_pk: int) -> None:
        """
        Project deletion with related entities takes too much time.
        Mark project as "Deleted" and move cascade deletion to the asynchronous job.
        """
        self.model.objects.filter(pk=project_pk).update(deleted=pendulum.now())
        cascade_delete_project_with_related_entities(project_pk)

    def add_users(self, project: Project, validated_data: Dict) -> None:
        users = validated_data.pop('users', [])
        for user in users:
            if user.status == user.Status.PENDING.value and not project.is_demo:
                raise ValidationError(_(f'You cannot adding user: {user.get_full_name()}'))
            project.users.add(user)

    def add_key_contacts(self, project: Project, validated_data: Dict) -> None:
        key_contacts = validated_data.pop('key_contacts')
        for key_contact in key_contacts:
            project.key_contacts.add(key_contact)

    def remove_users(self, project: Project, validated_data: Dict) -> None:
        users = validated_data.pop('users', [])
        for user in users:
            project.users.remove(user)
            project.key_contacts.remove(user)

    def remove_key_contacts(self, project: Project, validated_data: Dict) -> None:
        key_contacts = validated_data.pop('key_contacts')
        for key_contact in key_contacts:
            project.key_contacts.remove(key_contact)

    def generate_csv(self, request: Request) -> None:
        serializable_request = SerializableRequest(request)
        send_csv_report(serializable_request, Project, None, request.user.email)
