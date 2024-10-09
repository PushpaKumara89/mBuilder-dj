from api.queues.core.base import use_rq_if_configured

from api.queues.celery.m2m_post_delete import create_m2m_event as create_m2m_event_celery, \
    create_reverse_m2m_event as create_reverse_m2m_event_celery, \
    create_key_contacts_m2m_reverse_deletion_events as create_key_contacts_m2m_reverse_deletion_events_celery, \
    create_recipient_m2m_reverse_deletion_events as create_recipient_m2m_reverse_deletion_events_celery, \
    create_company_m2m_reverse_deletion_events as create_company_m2m_reverse_deletion_events_celery, \
    create_package_matrix_m2m_reverse_deletion_events as create_package_matrix_m2m_reverse_deletion_events_celery
from api.queues.rq.m2m_post_delete import create_m2m_event as create_m2m_event_rq, \
    create_reverse_m2m_event as create_reverse_m2m_event_rq, \
    create_key_contacts_m2m_reverse_deletion_events as create_key_contacts_m2m_reverse_deletion_events_rq, \
    create_recipient_m2m_reverse_deletion_events as create_recipient_m2m_reverse_deletion_events_rq, \
    create_company_m2m_reverse_deletion_events as create_company_m2m_reverse_deletion_events_rq, \
    create_package_matrix_m2m_reverse_deletion_events as create_package_matrix_m2m_reverse_deletion_events_rq

from api.models import User, Recipient, Company, PackageMatrix


@use_rq_if_configured(create_m2m_event_rq)
def create_m2m_event(**kwargs):
    create_m2m_event_celery.delay(**kwargs)


@use_rq_if_configured(create_reverse_m2m_event_rq)
def create_reverse_m2m_event(**kwargs):
    create_reverse_m2m_event_celery.delay(**kwargs)


@use_rq_if_configured(create_key_contacts_m2m_reverse_deletion_events_rq)
def create_key_contacts_m2m_reverse_deletion_events(instance: User):
    create_key_contacts_m2m_reverse_deletion_events_celery.delay(instance)


@use_rq_if_configured(create_recipient_m2m_reverse_deletion_events_rq)
def create_recipient_m2m_reverse_deletion_events(instance: Recipient):
    create_recipient_m2m_reverse_deletion_events_celery.delay(instance)


@use_rq_if_configured(create_company_m2m_reverse_deletion_events_rq)
def create_company_m2m_reverse_deletion_events(instance: Company):
    create_company_m2m_reverse_deletion_events_celery.delay(instance)


@use_rq_if_configured(create_package_matrix_m2m_reverse_deletion_events_rq)
def create_package_matrix_m2m_reverse_deletion_events(instance: PackageMatrix):
    create_package_matrix_m2m_reverse_deletion_events_celery.delay(instance)
