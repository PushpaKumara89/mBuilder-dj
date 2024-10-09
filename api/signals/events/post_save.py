from django.db.models.signals import post_save
from django.dispatch import receiver

from api.models import Subtask, Task, TaskUpdate, SubtaskUpdate, Package, PackageActivity, PackageActivityTask, \
    LocationMatrix, PackageMatrixHiddenActivityTask, PackageMatrix, Project, User, ProjectUser, Recipient, Media, \
    Company, PackageMatrixCompany, QualityIssue, QualityIssueUpdate, LocationMatrixPackage, ResponseCategory
from api.models.project_news import ProjectNews
from api.utilities.event_utilities import create_events_for_bulk_post_save, get_project_id


@receiver(post_save, sender=Company)
@receiver(post_save, sender=LocationMatrix)
@receiver(post_save, sender=LocationMatrixPackage)
@receiver(post_save, sender=Media)
@receiver(post_save, sender=Package)
@receiver(post_save, sender=PackageActivity)
@receiver(post_save, sender=PackageActivityTask)
@receiver(post_save, sender=PackageMatrix)
@receiver(post_save, sender=PackageMatrixCompany)
@receiver(post_save, sender=PackageMatrixHiddenActivityTask)
@receiver(post_save, sender=Project)
@receiver(post_save, sender=ProjectNews)
@receiver(post_save, sender=ProjectUser)
@receiver(post_save, sender=QualityIssue)
@receiver(post_save, sender=QualityIssueUpdate)
@receiver(post_save, sender=Recipient)
@receiver(post_save, sender=ResponseCategory)
@receiver(post_save, sender=Subtask)
@receiver(post_save, sender=SubtaskUpdate)
@receiver(post_save, sender=Task)
@receiver(post_save, sender=TaskUpdate)
@receiver(post_save, sender=User)
def on_entities_post_save(sender, instance, **kwargs):
    def safedelete_save():
        return not kwargs.get('created')\
               and not updated_fields\
               and (instance.deleted is not None
                    or instance.deleted is None)

    updated_fields = kwargs.get('update_fields')

    if not kwargs.get('raw', False) and not safedelete_save():
        kwargs['instances'] = [instance]
        kwargs['project_id'] = get_project_id(instance)

        create_events_for_bulk_post_save(**kwargs)
