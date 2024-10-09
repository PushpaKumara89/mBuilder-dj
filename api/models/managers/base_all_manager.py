from safedelete.managers import SafeDeleteAllManager

from api.models.managers.base_manager import BaseManager


class BaseAllManager(BaseManager, SafeDeleteAllManager):
    pass
