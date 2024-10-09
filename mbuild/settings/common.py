import mimetypes
import os

import environ

env = environ.Env()
# reading .env file
env.read_env(env.str('ENV_PATH', 'mbuild/.env'))

APP_URL = env.str('APP_URL', 'http://localhost')

ENV = env.str('ENV', 'local')
IS_TEST = ENV == 'testing'

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=True)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

# Application definition

INSTALLED_APPS = [
    'channels',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'api.apps.ApiConfig',
    'ws.apps.WSConfig',
    'rest_framework',
    'drf_yasg',
    'corsheaders',
    'phonenumber_field',
    'django_rest_passwordreset',
    'django_cron',
    'rest_framework_simplejwt.token_blacklist',
    'django_filters',
    'safedelete',
    'djmoney',
    'storages',
    'django_rq',
    'wkhtmltopdf',
    'rest_framework_mongoengine',
    'rest_framework_api_key',
    'reversion','drf_spectacular',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'api.http.middlewares.ResetPasswordAuthMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
]

ROOT_URLCONF = 'mbuild.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mbuild.wsgi.application'

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    # read os.environ['DATABASE_URL'] and raises ImproperlyConfigured exception if not found
    'default': env.db(),
    'mongodb': {
        'ENGINE': None
    }
}

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
    {'NAME': 'api.validators.DifferentPasswordValidator'}
]

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

PASSWORD_HASHERS = (
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
)

AUTH_USER_MODEL = 'api.User'

PHONENUMBER_DB_FORMAT = 'E164'

FRONTEND_URL = env.str('FRONTEND_URL', 'http://localhost')

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

REDIS_HOST = env.str('REDIS_HOST', 'redis://redis:6379')

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'{REDIS_HOST}/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

PRIVATE_MEDIA_URL_CACHE_LIFETIME = env.int('PRIVATE_MEDIA_URL_CACHE_LIFETIME', 60 * 50)  # 50 minutes
PRIVATE_REPORT_URL_CACHE_LIFETIME = env.int('PRIVATE_REPORT_URL_CACHE_LIFETIME', 60 * 60)  # 1 hour
PRIVATE_PROJECT_SNAPSHOT_URL_CACHE_LIFETIME = env.int('PRIVATE_PROJECT_SNAPSHOT_URL_CACHE_LIFETIME', 60 * 60)  # 1 hour

PROJECT_SNAPSHOT_GENERATION_DELAY_IN_MINUTES = env.int('PROJECT_SNAPSHOT_GENERATION_DELAY_IN_MINUTES', 60)

SUBTASK_DEFECT_STATUS_UPDATE_IN_MINUTES = env.int('SUBTASK_DEFECT_STATUS_UPDATE_IN_MINUTES', 60)

SUMMARY_RUN_AT_TIME = env.str('SUMMARY_RUN_AT_TIME', '17:00')

EXPORT_EVENTS = env.bool('EXPORT_EVENTS', False)

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

PROCESS_COMMANDS_SCHEDULE_IN_MINUTES = env.int('PROCESS_COMMANDS_SCHEDULE_IN_MINUTES', 1)

API_DOCUMENTATION_CREDENTIALS = env.str('API_DOCUMENTATION_CREDENTIALS', 'user:password')

PROJECTS_IDS_LIST_FOR_SNAPSHOTS = env.list('PROJECTS_IDS_LIST_FOR_SNAPSHOTS', default=[])
GENERATE_ONLY_JSON_SNAPSHOT = env.bool('GENERATE_ONLY_JSON_SNAPSHOT', False)

PDF_FILE_GENERATION_CHUNK_SIZE = env.int('PDF_FILE_GENERATION_CHUNK_SIZE', 100)
PDF_FILE_GENERATION_THREADS_BATCH_SIZE = env.int('PDF_FILE_GENERATION_THREADS_BATCH_SIZE', 8)

IMAGE_EXTENSIONS = tuple(ext.lstrip('.')
                         for ext in mimetypes.types_map
                         if mimetypes.types_map[ext].split('/')[0] == 'image')

VIDEO_EXTENSIONS = tuple(ext.lstrip('.')
                         for ext in mimetypes.types_map
                         if mimetypes.types_map[ext].split('/')[0] == 'video')

DATA_UPLOAD_MAX_NUMBER_FIELDS = 2000

HANDOVER_DOCUMENT_ARCHIVE_EXPIRATION_IN_DAYS = env.str('HANDOVER_DOCUMENT_ARCHIVE_EXPIRATION_IN_DAYS', 30)
HANDOVER_DOCUMENT_ARCHIVE_PART_SIZE_IN_GB = env.str('HANDOVER_DOCUMENT_ARCHIVE_PART_SIZE_IN_GB', 10)
HANDOVER_DOCUMENT_ARCHIVE_TEMP_FILE_FOLDER = env.str('HANDOVER_DOCUMENT_ARCHIVE_TEMP_FILE_FOLDER', '')

REST_FRAMEWORK = {
    # YOUR SETTINGS
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'recipe-app-api',
    'DESCRIPTION': 'Your project description',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    # OTHER SETTINGS
}