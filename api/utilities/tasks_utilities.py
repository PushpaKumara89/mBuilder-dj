from api.models import Task, TaskUpdate


def get_task_status(updating_activity_task):
    return Task.Statuses.NOT_APPLICABLE \
        if updating_activity_task.is_not_applicable_status_by_default \
        else Task.Statuses.OUTSTANDING


def create_task_updates(tasks):
    task_updates = []
    for created_task in tasks:
        task_updates.append(
            TaskUpdate(
                task=created_task,
                user=created_task.user,
                old_data={},
                new_data={'status': created_task.status}
            )
        )

    TaskUpdate.objects.bulk_create(task_updates, batch_size=500)


def modify_queryset(queryset, request):
    if request.query_params.get('all_with_activity'):
        queryset = Task.all_objects.all()

    if not request.query_params.get('sort'):
        queryset = queryset.order_by('building', 'level', 'area', 'package_activity')

    return queryset


class SerializableRequest:
    def __init__(self, request):
        self.parser_context = {'kwargs': request.parser_context['kwargs']}
        self.query_params = request.query_params
        self.user = request.user
