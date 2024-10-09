from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from safedelete import HARD_DELETE

from api.models import ProjectUser


UserModel = get_user_model()


class Command(BaseCommand):
    def handle(self, *args, **options):
        ProjectUser.objects.filter(user__group_id=UserModel.Group.COMPANY_ADMIN).delete(force_policy=HARD_DELETE)
