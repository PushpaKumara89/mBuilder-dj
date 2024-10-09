import uuid
from typing import Dict, Type

from api.models import ApiKey
from api.models.base_model import BaseModel
from api.services.base_entity_service import BaseEntityService


class ApiKeyEntityService(BaseEntityService):
    model: ApiKey = ApiKey

    def create(self, validated_data: Dict, **kwargs) -> Type[BaseModel]:
        validated_data['token'] = self._get_token()

        return super().create(validated_data, **kwargs)

    def _get_token(self) -> str:
        while True:
            token = uuid.uuid4().__str__()

            if self.model.objects.filter(token=token).exists():
                continue
            else:
                return token
