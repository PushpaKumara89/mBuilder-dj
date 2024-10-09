from rest_framework.request import Request

from api.models import LocationMatrix
from api.services.base_entity_service import BaseEntityService
from api.queues.send_report import send_csv_report
from api.utilities.tasks_utilities import SerializableRequest


class LocationMatrixEntityService(BaseEntityService):
    model = LocationMatrix

    def generate_csv(self, request: Request, project_id: int) -> None:
        serializable_request = SerializableRequest(request)
        send_csv_report(serializable_request, self.model, project_id, request.user.email)
