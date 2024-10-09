from django_filters import rest_framework

from api.models.project_news import ProjectNews


class ProjectNewsFilter(rest_framework.FilterSet):
    sort = rest_framework.OrderingFilter(
        fields=(
            ('title', 'title'),
        ),
    )

    class Meta:
        model = ProjectNews
        fields = ('title',)
