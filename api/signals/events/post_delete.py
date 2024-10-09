from django.db.models.signals import post_delete
from django.dispatch import receiver

from api.enums.entities import Entities
from api.models import Subtask, Task, TaskUpdate, SubtaskUpdate, Package, PackageActivity, PackageActivityTask, \
    LocationMatrix, PackageMatrix, PackageMatrixHiddenActivityTask, Project, User, Recipient, \
    Media, ProjectUser, Company, PackageMatrixCompany, LocationMatrixPackage, ResponseCategory
from api.models.project_news import ProjectNews
from api.queues.m2m_post_delete import create_key_contacts_m2m_reverse_deletion_events, \
    create_recipient_m2m_reverse_deletion_events, create_company_m2m_reverse_deletion_events, \
    create_package_matrix_m2m_reverse_deletion_events, create_m2m_event
from api.utilities.event_utilities import create_events_for_post_delete, get_project_id


@receiver(post_delete, sender=LocationMatrix)
@receiver(post_delete, sender=LocationMatrixPackage)
@receiver(post_delete, sender=Media)
@receiver(post_delete, sender=Package)
@receiver(post_delete, sender=PackageActivity)
@receiver(post_delete, sender=PackageActivityTask)
@receiver(post_delete, sender=PackageMatrix)
@receiver(post_delete, sender=PackageMatrixCompany)
@receiver(post_delete, sender=PackageMatrixHiddenActivityTask)
@receiver(post_delete, sender=ProjectNews)
@receiver(post_delete, sender=ProjectUser)
@receiver(post_delete, sender=ResponseCategory)
@receiver(post_delete, sender=Task)
def on_entities_post_delete(sender, instance, **kwargs):
    if not kwargs.get('raw', False):
        kwargs['instances'] = [instance]
        kwargs['project_id'] = get_project_id(instance)

        create_events_for_post_delete(**kwargs)


@receiver(post_delete, sender=Project)
def on_project_post_delete(sender, instance, **kwargs):
    if not kwargs.get('raw', False):
        kwargs['instances'] = [instance]
        kwargs['project_id'] = get_project_id(instance)

        create_m2m_event(instance=instance, relation='key_contacts', parent_entity_field='project',
                               action='post_remove', event_entity_name=Entities.PROJECT_KEY_CONTACTS.value,
                               child_entity_field='user', model=User)

        create_events_for_post_delete(**kwargs)


@receiver(post_delete, sender=Subtask)
def on_subtask_post_delete(sender, instance, **kwargs):
    if not kwargs.get('raw', False):
        kwargs['instances'] = [instance]
        kwargs['project_id'] = get_project_id(instance)

        create_m2m_event(instance=instance, relation='files', parent_entity_field='subtask',
                               action='post_remove', event_entity_name=Entities.SUBTASK_FILES.value,
                               child_entity_field='media', model=Media)

        create_events_for_post_delete(**kwargs)


@receiver(post_delete, sender=SubtaskUpdate)
def on_subtask_update_post_delete(sender, instance, **kwargs):
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


@receiver(post_delete, sender=TaskUpdate)
def on_task_update_post_delete(sender, instance, **kwargs):
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


@receiver(post_delete, sender=User)
def on_user_post_delete(sender, instance, **kwargs):
    if not kwargs.get('raw', False):
        kwargs['instances'] = [instance]
        kwargs['project_id'] = None

        create_key_contacts_m2m_reverse_deletion_events(instance)

        create_events_for_post_delete(**kwargs)


@receiver(post_delete, sender=Recipient)
def on_recipient_post_delete(sender, instance, **kwargs):
    if not kwargs.get('raw', False):
        kwargs['instances'] = [instance]
        kwargs['project_id'] = None

        create_recipient_m2m_reverse_deletion_events(instance)

        create_events_for_post_delete(**kwargs)


@receiver(post_delete, sender=Company)
def on_company_post_delete(sender, instance, **kwargs):
    if not kwargs.get('raw', False):
        kwargs['instances'] = [instance]
        kwargs['project_id'] = None

        create_company_m2m_reverse_deletion_events(instance)

        create_events_for_post_delete(**kwargs)


@receiver(post_delete, sender=PackageMatrix)
def on_package_matrix_post_delete(sender, instance, **kwargs):
    if not kwargs.get('raw', False):
        kwargs['instances'] = [instance]
        kwargs['project_id'] = None

        create_package_matrix_m2m_reverse_deletion_events(instance)

        create_events_for_post_delete(**kwargs)
