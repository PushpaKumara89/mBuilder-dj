from api.queues.core.base import use_rq_if_configured
from api.queues.celery.notify_company_admins_registration_user import \
    notify_company_admins_registration_user as notify_company_admins_registration_user_celery
from api.queues.rq.notify_company_admins_registration_user import \
    notify_company_admins_registration_user as notify_company_admins_registration_user_rq


@use_rq_if_configured(notify_company_admins_registration_user_rq)
def notify_company_admins_registration_user(user_id: int) -> None:
    notify_company_admins_registration_user_celery.delay(user_id)
