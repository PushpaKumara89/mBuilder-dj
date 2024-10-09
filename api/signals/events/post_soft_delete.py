from django.dispatch import receiver
from safedelete.signals import post_softdelete

from api.enums.entities import Entities
from api.models import Subtask, Task, TaskUpdate, SubtaskUpdate, Package, PackageActivity, PackageActivityTask, \
    LocationMatrix, PackageMatrixHiddenActivityTask, PackageMatrix, Project, User, Recipient, \
    Media, ProjectUser, Company, PackageMatrixCompany, QualityIssueUpdate, LocationMatrixPackage
from api.models.project_news import ProjectNews
from api.queues.m2m_post_delete import create_package_matrix_m2m_reverse_deletion_events, create_key_contacts_m2m_reverse_deletion_events, \
    create_m2m_event, create_company_m2m_reverse_deletion_events, create_recipient_m2m_reverse_deletion_events
from api.utilities.event_utilities import create_events_for_post_delete, get_project_id


@receiver(post_softdelete, sender=LocationMatrix)
@receiver(post_softdelete, sender=LocationMatrixPackage)
@receiver(post_softdelete, sender=Media)
@receiver(post_softdelete, sender=Package)
@receiver(post_softdelete, sender=PackageActivity)
@receiver(post_softdelete, sender=PackageActivityTask)
@receiver(post_softdelete, sender=PackageMatrixCompany)
@receiver(post_softdelete, sender=PackageMatrixHiddenActivityTask)
@receiver(post_softdelete, sender=ProjectNews)
@receiver(post_softdelete, sender=ProjectUser)
@receiver(post_softdelete, sender=Task)
def on_entities_post_soft_delete(sender, instance, **kwargs):
    if not kwargs.get('raw', False):
        kwargs['instances'] = [instance]
        kwargs['project_id'] = get_project_id(instance)

        create_events_for_post_delete(**kwargs)


@receiver(post_softdelete, sender=Project)
def on_project_post_soft_delete(sender, instance, **kwargs):
    if not kwargs.get('raw', False):
        kwargs['instances'] = [instance]
        kwargs['project_id'] = get_project_id(instance)

        create_m2m_event(instance=instance, relation='key_contacts', parent_entity_field='project',
                               action='post_remove', event_entity_name=Entities.PROJECT_KEY_CONTACTS.value,
                               child_entity_field='user', model=User)

        create_events_for_post_delete(**kwargs)


@receiver(post_softdelete, sender=Subtask)
def on_subtask_post_soft_delete(sender, instance, **kwargs):
    if not kwargs.get('raw', False):
        kwargs['instances'] = [instance]
        kwargs['project_id'] = get_project_id(instance)

        create_m2m_event(instance=instance, relation='files', parent_entity_field='subtask',
                               action='post_remove', event_entity_name=Entities.SUBTASK_FILES.value,
                               child_entity_field='media', model=Media)

        create_events_for_post_delete(**kwargs)


@receiver(post_softdelete, sender=SubtaskUpdate)
def on_subtask_update_post_soft_delete(sender, instance, **kwargs):
    if not kwargs.get('raw', False):
        kwargs['instances'] = [instance]
        kwargs['project_id'] = get_project_id(instance)

        create_m2m_event(instance=instance, relation='recipients', parent_entity_field='subtask_update',
                               action='post_remove', event_entity_name=Entities.SUBTASK_UPDATE_RECIPIENT.value,
                               child_entity_field='recipient', model=Recipient)

        create_m2m_event(instance=instance, relation='files', parent_entity_field='subtask_update',
                               action='post_remove', event_entity_name=Entities.SUBTASK_UPDATE_FILES.value,
                               child_entity_field='media', model=Media)

        create_events_for_post_delete(**kwargs)


@receiver(post_softdelete, sender=TaskUpdate)
def on_task_update_post_soft_delete(sender, instance, **kwargs):
    if not kwargs.get('raw', False):
        kwargs['instances'] = [instance]
        kwargs['project_id'] = get_project_id(instance)

        create_m2m_event(instance=instance, relation='recipients', parent_entity_field='task_update',
                               action='post_remove', event_entity_name=Entities.TASK_UPDATE_RECIPIENT.value,
                               child_entity_field='recipient', model=Recipient)

        create_m2m_event(instance=instance, relation='files', parent_entity_field='task_update',
                               action='post_remove', event_entity_name=Entities.TASK_UPDATE_FILES.value,
                               child_entity_field='media', model=Media)

        create_events_for_post_delete(**kwargs)


@receiver(post_softdelete, sender=QualityIssueUpdate)
def on_quality_issue_update_post_soft_delete(sender, instance, **kwargs):
    if not kwargs.get('raw', False):
        kwargs['instances'] = [instance]
        kwargs['project_id'] = get_project_id(instance)

        create_m2m_event(instance=instance, relation='recipients', parent_entity_field='quality_issue_update',
                               action='post_remove', event_entity_name=Entities.QUALITY_ISSUE_UPDATE_RECIPIENTS.value,
                               child_entity_field='recipient', model=Recipient)

        create_m2m_event(instance=instance, relation='files', parent_entity_field='quality_issue_update',
                               action='post_remove', event_entity_name=Entities.QUALITY_ISSUE_UPDATE_FILES.value,
                               child_entity_field='media', model=Media)

        create_events_for_post_delete(**kwargs)


@receiver(post_softdelete, sender=User)
def on_users_post_soft_delete(sender, instance, **kwargs):
    if not kwargs.get('raw', False):
        kwargs['instances'] = [instance]
        kwargs['project_id'] = None

        create_key_contacts_m2m_reverse_deletion_events(instance)

        create_events_for_post_delete(**kwargs)


@receiver(post_softdelete, sender=Recipient)
def on_recipient_post_soft_delete(sender, instance, **kwargs):
    if not kwargs.get('raw', False):
        kwargs['instances'] = [instance]
        kwargs['project_id'] = None

        create_recipient_m2m_reverse_deletion_events(instance)

        create_events_for_post_delete(**kwargs)


@receiver(post_softdelete, sender=Company)
def on_company_post_soft_delete(sender, instance, **kwargs):
    if not kwargs.get('raw', False):
        kwargs['instances'] = [instance]
        kwargs['project_id'] = None

        create_company_m2m_reverse_deletion_events(instance)

        create_events_for_post_delete(**kwargs)


@receiver(post_softdelete, sender=PackageMatrix)
def on_package_matrix_post_soft_delete(sender, instance, **kwargs):
    if not kwargs.get('raw', False):
        kwargs['instances'] = [instance]
        kwargs['project_id'] = None

        create_package_matrix_m2m_reverse_deletion_events(instance)

        create_events_for_post_delete(**kwargs)
