from django.conf import settings
from storages.backends.azure_storage import AzureStorage


class AzurePrivateMediaStorage(AzureStorage):
    account_name = settings.AZURE_ACCOUNT_NAME
    account_key = settings.AZURE_ACCOUNT_KEY
    azure_container = settings.AZURE_PRIVATE_MEDIA_CONTAINER
    expiration_secs = 3600
