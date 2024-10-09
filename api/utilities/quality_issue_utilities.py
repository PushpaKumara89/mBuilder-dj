from api.models import User


def apply_default_queryset_filters(kwargs, queryset, request):
    if 'project_pk' in kwargs:
        queryset = queryset.filter(location_matrix__project_id=kwargs['project_pk'])

    user = request.user
    if getattr(user, 'is_client', False):
        queryset = queryset.filter(user__group__in=[User.Group.CLIENT.value, User.Group.CONSULTANT.value])
    elif getattr(user, 'is_consultant', False):
        queryset = queryset.filter(user__company=user.company, user__group=User.Group.CONSULTANT.value)

    return queryset
