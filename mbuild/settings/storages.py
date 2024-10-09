import os

from mbuild.settings.common import env


AZURE_BASE_DOMAIN = env.str('AZURE_BASE_DOMAIN', 'core.windows.net')
AZURE_STATIC_CONTAINER = env.str('AZURE_STATIC_CONTAINER', '')
AZURE_MEDIA_CONTAINER = env.str('AZURE_MEDIA_CONTAINER', '')
AZURE_PRIVATE_MEDIA_CONTAINER = env.str('AZURE_PRIVATE_MEDIA_CONTAINER', '')
AZURE_PRIVATE_REPORT_CONTAINER = env.str('AZURE_PRIVATE_REPORT_CONTAINER', 'reports-dev')
AZURE_PRIVATE_PROJECT_SNAPSHOT_CONTAINER = env.str('AZURE_PRIVATE_PROJECT_SNAPSHOT_CONTAINER', '')

AZURE_ACCOUNT_NAME = os.getenv('AZURE_ACCOUNT_NAME', '')
AZURE_ACCOUNT_KEY = os.getenv('AZURE_ACCOUNT_KEY', '')

USE_EXTERNAL_FILES_STORAGE = env.bool('USE_EXTERNAL_FILES_STORAGE', False)
ACCOUNT_URL = f'{AZURE_ACCOUNT_NAME}.blob.{AZURE_BASE_DOMAIN}'

AZURE_CUSTOM_DOMAIN = env.str('AZURE_CUSTOM_DOMAIN', ACCOUNT_URL)

AZURE_BLOB_CONNECTION_STRING = ('AccountName=%s;'
                                'AccountKey=%s;'
                                'BlobEndpoint=%s;'
                                'EndpointSuffix=%s;'
                                'DefaultEndpointsProtocol=https;'
                                % (AZURE_ACCOUNT_NAME, AZURE_ACCOUNT_KEY, AZURE_CUSTOM_DOMAIN, AZURE_BASE_DOMAIN))

if USE_EXTERNAL_FILES_STORAGE:
    DEFAULT_FILE_STORAGE = 'api.storages.AzureMediaStorage'
    STATICFILES_STORAGE = 'api.storages.AzureStaticStorage'

    STATIC_URL = f'https://{AZURE_CUSTOM_DOMAIN}/{AZURE_STATIC_CONTAINER}/'
    MEDIA_URL = f'https://{AZURE_CUSTOM_DOMAIN}/{AZURE_MEDIA_CONTAINER}/'
else:
    STATIC_URL = 'static/'
    MEDIA_URL = 'http://localhost/media/'
    MEDIA_ROOT = 'media/'
    STATIC_ROOT = 'api/static'
