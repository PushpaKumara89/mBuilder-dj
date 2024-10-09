import os
from celery import Celery
from kombu import Queue

from mbuild.settings import AZURE_ACCOUNT_KEY, AZURE_ACCOUNT_NAME, AZURE_BASE_DOMAIN, REDIS_HOST
from mbuild.settings.common import env, ENV


AVAILABLE_ENVS = ['local', 'development', 'staging', 'testing', 'production']

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mbuild.settings')

app = Celery('mbuild')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.update(
    task_serializer='pickle',
    result_serializer='pickle',
    accept_content=['pickle'],
    broker_transport_options={'use_lock_renewal': True}
)

app.conf.task_queues = [
    Queue('default', no_ack=False),
    Queue('asset_handover_statistics', no_ack=False),
    Queue('handover_document', no_ack=False),
    Queue('handover_document_archive', no_ack=False),
    Queue('package_handover_statistics', no_ack=False),
    Queue('thumbnails', no_ack=False),
    Queue('summaries', no_ack=False),
    Queue('events', no_ack=False),
    Queue('floor_plan', no_ack=False),
    Queue('tasks', no_ack=False),
    Queue('reports', no_ack=False),
]

app.conf.imports = (
    'api.queues.celery.asset_handover',
    'api.queues.celery.asset_handover_statistics',
    'api.queues.celery.delete_related_to_hidden_qct_tasks',
    'api.queues.celery.destroy_project',
    'api.queues.celery.floor_plan',
    'api.queues.celery.handover_document',
    'api.queues.celery.handover_document_archive',
    'api.queues.celery.hard_delete_tasks',
    'api.queues.celery.m2m_post_delete',
    'api.queues.celery.media',
    'api.queues.celery.notify_company_admins_registration_user',
    'api.queues.celery.package_activity_tasks_hard_delete_related_qct',
    'api.queues.celery.package_handover',
    'api.queues.celery.package_handover_statistics',
    'api.queues.celery.quality_issue',
    'api.queues.celery.restore_related_to_hidden_qct_tasks',
    'api.queues.celery.restore_tasks_related_to_reinstated_location_matrix',
    'api.queues.celery.restore_tasks_related_to_reinstated_package_matrix',
    'api.queues.celery.send_report',
    'api.queues.celery.subtask_update',
    'api.queues.celery.subtasks',
    'api.queues.celery.summaries',
    'api.queues.celery.task',
    'api.queues.celery.task_update',
    'api.queues.celery.update_project_subtasks_defect_status',
)

app.conf.result_backend = REDIS_HOST
app.conf.broker_pool_limit = 0
app.conf.broker_channel_error_retry = True
app.conf.task_ignore_result = True
app.conf.task_store_errors_even_if_ignored = True

if ENV in AVAILABLE_ENVS and ENV != 'testing':
    SERVICE_BUS_SAS_POLICY_NAME = env.str('SERVICE_BUS_SAS_POLICY_NAME')
    SERVICE_BUS_SAS_KEY = env.str('SERVICE_BUS_SAS_KEY')
    SERVICE_BUS_NAMESPACE = env.str('SERVICE_BUS_NAMESPACE')

    app.conf.broker_url = f'azureservicebus://{SERVICE_BUS_SAS_POLICY_NAME}:{SERVICE_BUS_SAS_KEY}@{SERVICE_BUS_NAMESPACE}'

if ENV == 'testing':
    app.conf.task_always_eager = True
