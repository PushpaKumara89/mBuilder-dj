from django_filters import rest_framework
from django_filters.widgets import QueryArrayWidget

from api.http.filters.base_filters.char_in_filter import CharInFilter
from api.models import Recipient, Package, Task, User


class SubtaskUpdateRecipientsFilter(rest_framework.FilterSet):
    sort = rest_framework.OrderingFilter(
        fields=(
            ('email', 'email'),
            ('first_name', 'first_name'),
            ('last_name', 'last_name'),
        ),
    )

    building = CharInFilter(
        field_name='subtaskupdate__subtask__task__location_matrix__building',
        widget=QueryArrayWidget
    )
    area = CharInFilter(
        field_name='subtaskupdate__subtask__task__location_matrix__area',
        widget=QueryArrayWidget
    )
    level = CharInFilter(
        field_name='subtaskupdate__subtask__task__location_matrix__level',
        widget=QueryArrayWidget
    )
    package = rest_framework.ModelMultipleChoiceFilter(
        field_name='subtaskupdate__subtask__task__package_activity__packagematrix__package',
        widget=QueryArrayWidget,
        queryset=Package.objects.all()
    )
    task = rest_framework.ModelMultipleChoiceFilter(
        field_name='subtaskupdate__subtask__task',
        queryset=Task.objects.all(),
        widget=QueryArrayWidget
    )
    exclude_user_group = rest_framework.MultipleChoiceFilter(
        field_name='user__group',
        choices=(
            (1, User.Group.COMPANY_ADMIN.name,),
            (2, User.Group.ADMIN.name,),
            (3, User.Group.MANAGER.name,),
            (4, User.Group.SUBCONTRACTOR.name,),
        ),
        widget=QueryArrayWidget(),
        exclude=True
    )

    class Meta:
        model = Recipient
        fields = ('email', 'first_name', 'last_name',)
