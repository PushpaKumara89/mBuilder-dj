from mbuild.settings import app as celery_app

from api.queues.core.m2m_post_delete import create_m2m_event as create_m2m_event_core, \
    create_reverse_m2m_event as create_reverse_m2m_event_core, \
    create_key_contacts_m2m_reverse_deletion_events as create_key_contacts_m2m_reverse_deletion_events_core

from api.enums.entities import Entities
from api.models import User, Recipient, Company, PackageMatrix


@celery_app.task(queue='events', time_limit=3600)
def create_m2m_event(**kwargs):
    create_m2m_event_core(**kwargs)


@celery_app.task(queue='events', time_limit=3600)
def create_reverse_m2m_event(**kwargs):
    create_reverse_m2m_event_core(**kwargs)


@celery_app.task(queue='events', time_limit=3600)
def create_key_contacts_m2m_reverse_deletion_events(instance: User):
    create_key_contacts_m2m_reverse_deletion_events_core(instance)


@celery_app.task(queue='events', time_limit=3600)
def create_recipient_m2m_reverse_deletion_events(instance: Recipient):
    task_updates = instance.taskupdate_set.all()
    subtask_updates = instance.subtaskupdate_set.all()

    create_reverse_m2m_event.delay(child_instance=instance, parent_instances=task_updates, action='post_remove',
                                   parent_entity_field='task_update', child_entity_field='recipient',
                                   event_entity_name=Entities.TASK_UPDATE_RECIPIENT.value, model=Recipient)

    create_reverse_m2m_event.delay(child_instance=instance, parent_instances=subtask_updates, action='post_remove',
                                   parent_entity_field='subtask_update', child_entity_field='recipient',
                                   event_entity_name=Entities.SUBTASK_UPDATE_RECIPIENT.value, model=Recipient)


@celery_app.task(queue='events', time_limit=3600)
def create_company_m2m_reverse_deletion_events(instance: Company):
    package_matrix_companies = instance.packagematrixcompany_set.all()

    create_reverse_m2m_event.delay(child_instance=instance, parent_instances=package_matrix_companies, action='post_remove',
                                   parent_entity_field='package_matrix_company', child_entity_field='company',
                                   event_entity_name=Entities.PACKAGE_MATRIX_COMPANY.value, model=Company)


@celery_app.task(queue='events', time_limit=3600)
def create_package_matrix_m2m_reverse_deletion_events(instance: PackageMatrix):
    package_matrix_companies = instance.packagematrixcompany_set.all()

    create_reverse_m2m_event.delay(child_instance=instance, parent_instances=package_matrix_companies, action='post_remove',
                                   parent_entity_field='package_matrix_company', child_entity_field='package_matrix',
                                   event_entity_name=Entities.PACKAGE_MATRIX_COMPANY.value, model=PackageMatrix)
