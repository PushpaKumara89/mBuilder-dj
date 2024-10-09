from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from api.enums.entities import Entities
from api.models import Project, TaskUpdate, SubtaskUpdate, Subtask, User, PackageActivity, QualityIssueUpdate, \
    QualityIssue
from api.utilities.event_utilities import perform_event_creation, perform_group_event_creation


@receiver(m2m_changed, sender=Project.users.through)
def on_project_users_changed(sender, **kwargs):
    perform_event_creation('project', 'user', Entities.PROJECT_USER.value, kwargs)


@receiver(m2m_changed, sender=PackageActivity.files.through)
def on_package_activity_files_changed(sender, **kwargs):
    perform_event_creation('project', 'user', Entities.PACKAGE_ACTIVITY_FILES.value, kwargs)


@receiver(m2m_changed, sender=Project.key_contacts.through)
def on_project_key_contacts_changed(sender, **kwargs):
    perform_event_creation('project', 'user', Entities.PROJECT_KEY_CONTACTS.value, kwargs)


@receiver(m2m_changed, sender=TaskUpdate.files.through)
def on_task_update_files_changed(sender, **kwargs):
    perform_event_creation('task_update', 'media', Entities.TASK_UPDATE_FILES.value, kwargs)


@receiver(m2m_changed, sender=SubtaskUpdate.files.through)
def on_subtask_update_files_changed(sender, **kwargs):
    perform_event_creation('subtask_update', 'media', Entities.SUBTASK_UPDATE_FILES.value, kwargs)


@receiver(m2m_changed, sender=TaskUpdate.recipients.through)
def on_task_update_recipient_changed(sender, **kwargs):
    perform_event_creation('task_update', 'recipient', Entities.TASK_UPDATE_RECIPIENT.value, kwargs)


@receiver(m2m_changed, sender=QualityIssueUpdate.recipients.through)
def on_quality_issue_update_recipient_changed(sender, **kwargs):
    perform_event_creation('quality_issue_update', 'recipient', Entities.QUALITY_ISSUE_UPDATE_RECIPIENTS.value, kwargs)


@receiver(m2m_changed, sender=QualityIssueUpdate.files.through)
def on_quality_issue_update_files_changed(sender, **kwargs):
    perform_event_creation('quality_issue_update', 'media', Entities.QUALITY_ISSUE_UPDATE_FILES.value, kwargs)


@receiver(m2m_changed, sender=QualityIssue.attachments.through)
def on_quality_issue_files_changed(sender, **kwargs):
    perform_event_creation('quality_issue', 'media', Entities.QUALITY_ISSUE_ATTACHMENTS.value, kwargs)


@receiver(m2m_changed, sender=SubtaskUpdate.recipients.through)
def on_subtask_update_recipient_changed(sender, **kwargs):
    perform_event_creation('subtask_update', 'recipient', Entities.SUBTASK_UPDATE_RECIPIENT.value, kwargs)


@receiver(m2m_changed, sender=Subtask.files.through)
def on_subtask_files_changed(sender, **kwargs):
    perform_event_creation('subtask', 'media', Entities.SUBTASK_FILES.value, kwargs)


@receiver(m2m_changed, sender=User.groups.through)
def on_user_group_changed(sender, **kwargs):
    perform_group_event_creation(Entities.USER_GROUPS.value, kwargs)
