from api.models import User, PackageHandoverDocumentMedia
from django.db.models import Q


def get_consultant_company_filter_query(user: User):
    return Q(
        packagehandoverdocumentmediaupdate__new_data__status=PackageHandoverDocumentMedia.Status.IN_PROGRESS.value,
        packagehandoverdocumentmediaupdate__user__company_id=user.company_id,
        packagehandoverdocumentmediaupdate__user__group=User.Group.CONSULTANT.value
    )
