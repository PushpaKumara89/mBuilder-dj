from corsheaders.defaults import default_methods, default_headers

from mbuild.settings.common import env


CORS_ORIGIN_WHITELIST = env.tuple('CORS_ORIGIN_WHITELIST', default=())
CORS_ORIGIN_ALLOW_ALL = env.bool('CORS_ORIGIN_ALLOW_ALL', default=False)
CORS_ALLOW_METHODS = env.tuple('CORS_ALLOW_METHODS', default=default_methods)
CORS_ALLOW_HEADERS = default_headers + env.tuple('CORS_ALLOW_HEADERS', default=()) + (
    'access-control-expose-headers',
    'Access-Control-Allow-Origin',
    'cache-control',
    'if-none-match',
    'sentry-trace'
)
CORS_EXPOSE_HEADERS = env.tuple('CORS_EXPOSE_HEADERS', default=())
CORS_ALLOW_CREDENTIALS = env.bool('CORS_ALLOW_CREDENTIALS', default=False)
