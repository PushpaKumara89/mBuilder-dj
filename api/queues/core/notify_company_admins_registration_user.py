from django.contrib.auth import get_user_model

from api.mails.user.notify_company_admins_registration_user import NotifyCompanyAdminsRegistrationUser


UserModel = get_user_model()


def notify_company_admins_registration_user(user_id: int) -> None:
    admin_emails = UserModel.objects\
        .filter(deleted__isnull=True, group_id=UserModel.Group.COMPANY_ADMIN, email__isnull=False)\
        .values_list('email', flat=True)
    user = UserModel.objects.get(id=user_id)
    NotifyCompanyAdminsRegistrationUser().set_context({'user': user}).set_to(list(admin_emails)).send()
