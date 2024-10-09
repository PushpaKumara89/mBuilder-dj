from django.dispatch import receiver
from safedelete.signals import post_undelete

from api.models import Task, TaskUpdate, Subtask, SubtaskUpdate, Package, PackageActivity, PackageActivityTask, \
    LocationMatrix, PackageMatrix, PackageMatrixHiddenActivityTask, Project, User, Recipient, \
    Media, ProjectUser, Company, PackageMatrixCompany, QualityIssue, LocationMatrixPackage
from api.models.project_news import ProjectNews
from api.utilities.event_utilities import create_events_for_bulk_post_save, get_project_id


@receiver(post_undelete, sender=Company)
@receiver(post_undelete, sender=LocationMatrix)
@receiver(post_undelete, sender=LocationMatrixPackage)
@receiver(post_undelete, sender=Media)
@receiver(post_undelete, sender=Package)
@receiver(post_undelete, sender=PackageActivity)
@receiver(post_undelete, sender=PackageActivityTask)
@receiver(post_undelete, sender=PackageMatrix)
@receiver(post_undelete, sender=PackageMatrixCompany)
@receiver(post_undelete, sender=PackageMatrixHiddenActivityTask)
@receiver(post_undelete, sender=Project)
@receiver(post_undelete, sender=ProjectNews)
@receiver(post_undelete, sender=ProjectUser)
@receiver(post_undelete, sender=QualityIssue)
@receiver(post_undelete, sender=Recipient)
@receiver(post_undelete, sender=Subtask)
@receiver(post_undelete, sender=SubtaskUpdate)
@receiver(post_undelete, sender=Task)
@receiver(post_undelete, sender=TaskUpdate)
@receiver(post_undelete, sender=User)
def on_entities_post_undelete(sender, instance, **kwargs):
    if not kwargs.get('raw', False):
        kwargs['instances'] = [instance]
        kwargs['project_id'] = get_project_id(instance)

        create_events_for_bulk_post_save(**kwargs)
