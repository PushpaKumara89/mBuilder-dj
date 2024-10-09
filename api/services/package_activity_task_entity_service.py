from typing import Dict, Union, Optional, List

from django.contrib.auth import get_user_model

from api.models import PackageActivityTask, PackageMatrixHiddenActivityTask
from api.services.base_entity_service import BaseEntityService
from api.queues.delete_related_to_hidden_qct_tasks import delete_related_to_hidden_qct_tasks
from api.queues.restore_related_to_hidden_qct_tasks import restore_related_to_hidden_qct_tasks
from api.services.package_activity_task_entity_sync_service import PackageActivityTaskEntitySyncService


User = get_user_model()


class PackageActivityTaskEntityService(BaseEntityService):
    model: PackageActivityTask = PackageActivityTask
    sync_service: PackageActivityTaskEntitySyncService = PackageActivityTaskEntitySyncService

    def sync(self, validated_data: List[Dict], initial_data: List[Dict], sync_config: Dict = None) -> None:
        sync_config = sync_config or {}
        if 'fields_to_update' not in sync_config:
            sync_config['fields_to_update'] = ['description', 'order', 'is_not_applicable_status_by_default',
                                               'is_photo_required', 'photo_requirement_comment', 'is_default_for_subtask']
        sync_service = self._get_sync_service(model=self.model, validated_data=validated_data, initial_data=initial_data, **sync_config)
        sync_service.sync()

    def hide_package_matrix_task(self, validated_data: Dict) -> None:
        hidden_task = PackageMatrixHiddenActivityTask.objects.create(**validated_data)
        delete_related_to_hidden_qct_tasks({
            'package_activity_task_id': validated_data['package_activity_task'],
            'location_matrix__project__pk': hidden_task.package_matrix.project_id
        })

    def show_package_matrix_task(self, validated_data: Dict, user: User, project_pk: Optional[Union[int, str]]) -> None:
        PackageMatrixHiddenActivityTask.objects.filter(**validated_data).delete()
        restore_related_to_hidden_qct_tasks(validated_data['package_activity_task'],
                                                  project_pk,
                                                  validated_data['package_matrix'],
                                                  user)
