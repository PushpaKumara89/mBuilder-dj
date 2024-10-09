from datetime import timedelta

from mbuild.settings.common import env


REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
        'rest_framework_api_key.permissions.HasAPIKey',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'api.authentication.query_string.JWTAuthenticationQueryString',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
    'TEST_REQUEST_RENDERER_CLASSES': (
        'rest_framework.renderers.MultiPartRenderer',
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.TemplateHTMLRenderer',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'EXCEPTION_HANDLER': 'api.exceptions.custom_exception_handler',
    'UNAUTHENTICATED_USER': 'api.models.anonymous_user.AnonymousUser',
}


SWAGGER_SETTINGS = {
    'LOGIN_URL': '/admin/login',
    'LOGOUT_URL': '/admin/logout'
}


SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=env.int('ACCESS_TOKEN_LIFETIME_IN_MINUTES', 1440)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=env.int('REFRESH_TOKEN_LIFETIME_IN_DAYS', 7)),
}


DJANGO_REST_PASSWORDRESET_NO_INFORMATION_LEAKAGE = True
DJANGO_REST_MULTITOKENAUTH_RESET_TOKEN_EXPIRY_TIME = env.int('DJANGO_REST_MULTITOKENAUTH_RESET_TOKEN_EXPIRY_TIME', 1)
RESET_TOKEN_EXPIRY_TIME_FOR_USER_WITHOUT_PASSWORD = {'months': 1}
RESET_TOKEN_EXPIRY_TIME_FOR_USER_WITH_PASSWORD = {'hours': DJANGO_REST_MULTITOKENAUTH_RESET_TOKEN_EXPIRY_TIME}
