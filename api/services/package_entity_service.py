from typing import Dict, List

from rest_framework.request import Request

from api.models import Package
from api.services.base_entity_service import BaseEntityService
from api.utilities.tasks_utilities import SerializableRequest
from api.queues.send_report import send_csv_report


class PackageEntityService(BaseEntityService):
    model: Package = Package

    def sync(self, validated_data: List[Dict], initial_data: List[Dict], sync_config: Dict = None) -> None:
        sync_config = sync_config or {}
        if 'fields_to_update' not in sync_config:
            sync_config['fields_to_update'] = ['name', 'order']
        sync_service = self._get_sync_service(model=self.model, validated_data=validated_data, initial_data=initial_data, **sync_config)
        sync_service.sync(delete_nonexistent=False)

    def sync_delete_nonexistent(self, initial_data: List[Dict]) -> None:
        sync_service = self._get_sync_service(model=self.model, initial_data=initial_data)
        sync_service.delete_nonexistent()

    def generate_csv(self, request: Request) -> None:
        serializable_request = SerializableRequest(request)
        send_csv_report(serializable_request, self.model, None, request.user.email)
