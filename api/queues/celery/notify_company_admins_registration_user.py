from mbuild.settings import app as celery_app

from api.queues.core.notify_company_admins_registration_user import \
    notify_company_admins_registration_user as notify_company_admins_registration_user_core


@celery_app.task(queue='default')
def notify_company_admins_registration_user(user_id: int) -> None:
    notify_company_admins_registration_user_core(user_id)
