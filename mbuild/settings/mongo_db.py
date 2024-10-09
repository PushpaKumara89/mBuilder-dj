import mongoengine

from mbuild.settings.common import env


MONGO_DSN = env.str('MONGO_DSN', None)

if not MONGO_DSN:
    MONGO_HOST_PREFIX = env.str('MONGO_HOST_PREFIX', 'mongodb')
    MONGO_USER = env.str('MONGO_USER')
    MONGO_PASS = env.str('MONGO_PASSWORD')
    MONGO_HOST = env.str('MONGO_HOST')
    MONGO_DB_NAME = env.str('MONGO_DB_NAME')
    MONGO_AUTH_SOURCE = env.str('MONGO_AUTH_SOURCE', 'admin')
    MONGO_DSN = '%s://%s:%s@%s/%s?authSource=%s' % (MONGO_HOST_PREFIX, MONGO_USER, MONGO_PASS, MONGO_HOST, MONGO_DB_NAME, MONGO_AUTH_SOURCE)

mongoengine.connect(host=MONGO_DSN)
