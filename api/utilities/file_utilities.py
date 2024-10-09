from typing import Optional

from django.core.files.base import ContentFile
from sentry_sdk import capture_exception

from api.utilities.storage_utilities import get_common_storage


def copy_file_by_link(file_link: str, file_name: str, is_public: bool) -> Optional[ContentFile]:
    media_storage = get_common_storage(is_public)
    try:
        file = media_storage.open(file_link)
    except BaseException as e:
        capture_exception(e)
        return None

    new_file = ContentFile(file.read())
    new_file.name = file_name

    return new_file
