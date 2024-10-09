from mbuild.settings.common import env


CHANNEL_LAYERS = {}
WEBSOCKET_PORT = env.int('WEBSOCKET_PORT', 8888)
EDIT_MODE_CLOSE_IN_MINUTES = env.int('EDIT_MODE_CLOSE_IN_MINUTES', 5)
ASGI_APPLICATION = 'mbuild.asgi.application'
