from typing import Any

from django.core.files.storage import default_storage

from api.storages import AzurePrivateMediaStorage


def get_common_storage(is_public: bool) -> Any:
    return default_storage if is_public else AzurePrivateMediaStorage()
