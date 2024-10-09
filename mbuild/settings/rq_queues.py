from mbuild.settings.common import ENV, REDIS_HOST

AVAILABLE_ENVS = ['production']

# Configuration for plain python RQ
REDIS_URL = REDIS_HOST

RQ_QUEUES = {
    'commands-project-*': {
        'URL': '%s/0' % REDIS_HOST,
        'DEFAULT_TIMEOUT': 0
    },
}

if ENV == 'testing':
    for queue_name, settings in RQ_QUEUES.items():
        settings['ASYNC'] = False
