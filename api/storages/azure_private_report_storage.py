from django.conf import settings
from storages.backends.azure_storage import AzureStorage


class AzurePrivateReportStorage(AzureStorage):
    def __init__(self, **kwargs):
        kwargs['upload_max_conn'] = 1
        super().__init__(**kwargs)

    account_name = settings.AZURE_ACCOUNT_NAME
    account_key = settings.AZURE_ACCOUNT_KEY
    azure_container = settings.AZURE_PRIVATE_REPORT_CONTAINER
    expiration_secs = 3600
