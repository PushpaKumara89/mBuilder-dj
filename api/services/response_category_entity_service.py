from api.models import ResponseCategory
from api.services.base_entity_service import BaseEntityService


class ResponseCategoryEntityService(BaseEntityService):
    model: ResponseCategory = ResponseCategory
