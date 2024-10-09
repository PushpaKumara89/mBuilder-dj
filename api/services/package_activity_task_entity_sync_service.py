from api.models import PackageMatrixHiddenActivityTask, PackageMatrix
from api.services.base_entity_sync_service import BaseEntitySyncService
from api.queues.package_activity_tasks_hard_delete_related_qct import package_activity_tasks_hard_delete_related_qct


class PackageActivityTaskEntitySyncService(BaseEntitySyncService):
    def __init__(self, *args, **kwargs) -> None:
        self.package_activity_id = kwargs.pop('package_activity_id')
        super().__init__(*args, **kwargs)

    def _create_entities(self) -> None:
        new_entities = [self.model(package_activity_id=self.package_activity_id, **entity_data)
                        for entity_data in self.new_entities_data]
        tasks = self.model.objects.bulk_create(new_entities)

        package_matrices = PackageMatrix.objects.filter(package_activity_id=self.package_activity_id).all()
        hidden_activity_tasks = []

        for task in tasks:
            for package_matrix in package_matrices:
                hidden_activity_tasks.append(PackageMatrixHiddenActivityTask(package_activity_task=task,
                                                                             package_matrix=package_matrix))

        PackageMatrixHiddenActivityTask.objects.bulk_create(hidden_activity_tasks)

    def delete_nonexistent(self) -> None:
        data = self.initial_data if hasattr(self, 'initial_data') else []
        existing_ids = [entity['id'] for entity in data if 'id' in entity]
        filter_parameters = {'package_activity_id': self.package_activity_id}

        self.model.objects.exclude(pk__in=existing_ids).filter(**filter_parameters).delete()

        package_activity_tasks_hard_delete_related_qct(filter_parameters, {'package_activity_task_id__in': existing_ids})
