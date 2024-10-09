from safedelete.managers import SafeDeleteDeletedManager

from api.models.managers.base_manager import BaseManager


class BaseDeletedManager(BaseManager, SafeDeleteDeletedManager):
    pass
