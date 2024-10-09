import sentry_sdk
from azure.servicebus._pyamqp.error import AMQPConnectionError
from azure.servicebus.exceptions import ServiceBusConnectionError
from sentry_sdk.integrations.django import DjangoIntegration

from mbuild.settings.common import env, ENV

SENTRY_DSN = env.str('SENTRY_DSN', None)
if SENTRY_DSN is not None:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=ENV,
        integrations=[DjangoIntegration()],
        ignore_errors=[AMQPConnectionError, ServiceBusConnectionError]
    )
