from django_filters import rest_framework

from api.models.edit_mode import EditMode


class EditModeFilter(rest_framework.FilterSet):
    sort = rest_framework.OrderingFilter(
        fields=(
            ('project', 'project',),
            ('entity', 'entity',),
            ('entity_id', 'entity_id',),
        ),
    )

    project = rest_framework.CharFilter(field_name='project')
    entity = rest_framework.CharFilter(field_name='entity')
    entity_id = rest_framework.NumberFilter(field_name='entity_id')

    class Meta:
        model = EditMode
        fields = ('project', 'entity', 'entity_id',)
