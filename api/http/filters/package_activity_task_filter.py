from django_filters import rest_framework

from api.models import PackageActivity
from api.models.package_activity_task import PackageActivityTask


class PackageActivityTaskFilter(rest_framework.FilterSet):
    sort = rest_framework.OrderingFilter(
        fields=(
            ('order', 'order'),
            ('package_activity__name', 'package_activity_name')
        ),
    )

    package_activity = rest_framework.ModelMultipleChoiceFilter(field_name='package_activity',
                                                                queryset=PackageActivity.objects.all())

    is_default_for_subtask = rest_framework.BooleanFilter(field_name='is_default_for_subtask')

    class Meta:
        model = PackageActivityTask
        fields = ('order',)
