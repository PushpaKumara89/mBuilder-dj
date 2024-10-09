from typing import Dict, List, Union

from rest_framework.request import Request

from api.models import PackageActivity, PackageActivityTask
from api.services.base_entity_service import BaseEntityService
from api.services.package_activity_task_entity_service import PackageActivityTaskEntityService
from api.queues.send_report import send_csv_report
from api.utilities.tasks_utilities import SerializableRequest


class PackageActivityEntityService(BaseEntityService):
    model: PackageActivity = PackageActivity

    def create(self, validated_data: Dict) -> PackageActivity:
        activity_tasks = validated_data.pop('packageactivitytask_set')
        files = validated_data.pop('files', None)

        package_activity = self.model.objects.create(**validated_data)

        if files:
            package_activity.files.set(files)

        if activity_tasks:
            PackageActivityTask.objects.bulk_create(
                [PackageActivityTask(package_activity=package_activity, **item) for item in activity_tasks]
            )

        return package_activity

    def update(self, instance: PackageActivity, validated_data: Dict) -> PackageActivity:
        activity_tasks = validated_data.pop('packageactivitytask_set')
        files = validated_data.pop('files') if 'files' in validated_data else []

        if self._has_default_for_subtask(activity_tasks):
            instance.packageactivitytask_set.update(is_default_for_subtask=False)

        instance.files.set(files)

        self._sync_activity_tasks(activity_tasks, instance.pk)

        return super().update(instance, validated_data)

    @staticmethod
    def _has_default_for_subtask(activity_tasks: List) -> bool:
        for activity_task in activity_tasks:
            if activity_task.get('is_default_for_subtask'):
                return True
        return False

    def _sync_activity_tasks(self, validated_data: List, parent_id: Union[int, str]) -> None:
        for activity_task in validated_data:
            if 'package_activity' in activity_task:
                activity_task['package_activity_id'] = activity_task.pop('package_activity').pk

        PackageActivityTaskEntityService().sync(validated_data=validated_data,
                                                initial_data=validated_data,
                                                sync_config={'package_activity_id': parent_id})

    def generate_csv(self, request: Request) -> None:
        serializable_request = SerializableRequest(request)
        send_csv_report(serializable_request, self.model, None, request.user.email)
