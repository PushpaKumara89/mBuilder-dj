import pendulum
from django.conf import settings
from django.db.models import Q
from django.urls import reverse
from django.utils.translation import gettext as _

from api.mails import TaskStatusChanged
from api.models import Task, User
from api.utilities.time_utilities import change_timezone_to_london


def send_task_status_changed_email_notification(task_update):
    def get_subject():
        return _('MBuild – Urgent Attention, Immediate Response Required – %s, %s - %s - %s' % (project_name, building, level, area)) \
            if len(to_recipients) > 0 \
            else _('MBuild – Quality Critical Task Statused – %s, %s - %s - %s' % (project_name, building, level, area))

    task = task_update.task
    task_update_user = task_update.user
    location_matrix = task.location_matrix

    to_recipients = [recipient.email for recipient in task_update.recipients.all()]
    to_multiplex = list(User.objects.filter(Q(Q(is_superuser=True) | Q(groups=User.Group.COMPANY_ADMIN.value)) &
                                            ~Q(email__in=to_recipients)).all().values_list('email', flat=True))
    has_subcontractor_in_recipients = User.objects.filter(groups=User.Group.SUBCONTRACTOR.value,
                                                          email__in=to_recipients).exists()
    project_name = location_matrix.project.name
    package_name = location_matrix.locationmatrixpackage_set.filter(
        package_activity__pk=task.package_activity.pk
    ).get().package.name

    building = location_matrix.building
    area = location_matrix.area
    level = location_matrix.level

    task_update_comment = task_update.comment

    identified_by = '%s %s' % (task_update_user.first_name, task_update_user.last_name)
    identified_on = change_timezone_to_london(task_update.created_at)
    identified_on = pendulum.from_timestamp(identified_on.timestamp()).strftime('%b %d, %Y %I:%m %p')

    initializer_email = task_update_user.email
    initializer_phone = task_update_user.phone

    package_activity_name = task.package_activity.name
    package_activity_task_description = task.package_activity_task.description

    app_url = settings.APP_URL

    links = [
        {'name': 'Photo ' + str(num), 'url': app_url + reverse('media_private_retrieve', kwargs={'uuid': file.hash})}
        for num, file
        in enumerate(task_update.files.all(), start=1)
    ]

    context = {
        'area': area,
        'building': building,
        'identified_by': identified_by,
        'identified_on': identified_on,
        'initializer_email': initializer_email,
        'initializer_phone': initializer_phone,
        'level': level,
        'links': links,
        'package_activity_name': package_activity_name,
        'package_activity_task_description': package_activity_task_description,
        'package_name': package_name,
        'project_name': project_name,
        'status': task.status,
        'status_name': Task.Statuses[task.status.upper()].label,
        'task_id': task.id,
        'task_update_comment': task_update_comment,
    }

    TaskStatusChanged() \
        .set_subject(get_subject()) \
        .set_to(to_multiplex) \
        .set_reply_to(task_update_user.email) \
        .set_context(context) \
        .send()

    if len(to_recipients) > 0:
        TaskStatusChanged() \
            .set_subject(get_subject()) \
            .set_to(to_recipients) \
            .set_reply_to(task_update_user.email) \
            .set_context({**context, 'has_subcontractor_in_recipients': has_subcontractor_in_recipients}) \
            .send()
