from api.models import AssetRegister
from api.services.base_entity_service import BaseEntityService


class AssetRegisterEntityService(BaseEntityService):
    model: AssetRegister = AssetRegister
