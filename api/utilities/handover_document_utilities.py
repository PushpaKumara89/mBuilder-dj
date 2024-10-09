import uuid

from django.db.models import Q, Exists, OuterRef
from django_filters import rest_framework

from api.models import HandoverDocument, User, PackageMatrixCompany, PackageHandoverDocumentMedia
from api.utilities.query_params_utilities import clean_query_param
from api.utilities.helpers import get_int_array_parameter, get_array_parameter


def add_document_type_filters(request, filters: list, handover_document_path = None) -> None:
    if handover_document_path is None:
        handover_document_path = ''
    else:
        handover_document_path = f'{handover_document_path}__'

    asset_handover_document_types = get_int_array_parameter('asset_handover_document_type', request.query_params)
    package_handover_document_types = get_int_array_parameter('package_handover_document_type', request.query_params)

    if asset_handover_document_types or package_handover_document_types:
        document_type_filters = None
        asset_handover_filter = Q(
            **{
                f'{handover_document_path}entity': HandoverDocument.Entities.ASSET_HANDOVER,
                f'{handover_document_path}document_type__in': asset_handover_document_types
            }
        )
        package_handover_filter = Q(
            **{
                f'{handover_document_path}entity': HandoverDocument.Entities.PACKAGE_HANDOVER,
                f'{handover_document_path}document_type__in': package_handover_document_types
            }
        )

        if asset_handover_document_types:
            document_type_filters = asset_handover_filter

        if package_handover_document_types:
            if document_type_filters is None:
                document_type_filters = package_handover_filter
            else:
                document_type_filters |= package_handover_filter

        if document_type_filters is not None:
            filters.append(document_type_filters)


def add_filters_by_user_role(user: User, handover_documents_filters: list, project_pk: int):
    if user.is_consultant:
        handover_documents_filters.append(
            Q(
                company=user.company,
                entity=HandoverDocument.Entities.PACKAGE_HANDOVER
            ) |
            Q(
                entity=HandoverDocument.Entities.ASSET_HANDOVER
            )
        )

    if user.is_subcontractor:
        handover_documents_filters.append(
            Exists(PackageMatrixCompany.objects.filter(
                package_matrix__package=OuterRef('package'),
                package_matrix__package_activity=OuterRef('package_activity'),
                package_matrix__project=project_pk,
                company=OuterRef('company'),
                deleted__isnull=True,
                company_id=user.company.id
            ))
        )


def add_filters_by_locations(request, handover_document_filters: list, project_pk: int, handover_document_path: str = None) -> None:
    if handover_document_path is None:
        handover_document_path = ''
    else:
        handover_document_path = f'{handover_document_path}__'

    asset_handover_kwfilters = {f'{handover_document_path}entity': HandoverDocument.Entities.ASSET_HANDOVER}
    package_handover_kwfilters = {f'{handover_document_path}entity': HandoverDocument.Entities.PACKAGE_HANDOVER}
    location_matrix_package_kwfilters = {
        'id': OuterRef(f'{handover_document_path}entity_id'),
        'deleted__isnull': True,
        'package_handover_document__deleted__isnull': True,
        'package_handover_document__package_handover__deleted__isnull': True,
        'package_handover_document__package_handover__package_matrix__deleted__isnull': True,
        'package_handover_document__package_handover__package_matrix__locationmatrixpackage__deleted__isnull': True,
        'package_handover_document__package_handover__package_matrix__locationmatrixpackage__location_matrix__deleted__isnull': True,
        'package_handover_document__package_handover__package_matrix__locationmatrixpackage__enabled': True,
        'package_handover_document__package_handover__package_matrix__locationmatrixpackage__location_matrix__project': project_pk,
        'package_handover_document__package_handover__package_matrix__project': project_pk,
    }
    buildings = clean_query_param(
        get_array_parameter('building', request.query_params),
        rest_framework.CharFilter
    )
    levels = clean_query_param(
        get_array_parameter('level', request.query_params),
        rest_framework.CharFilter
    )
    areas = clean_query_param(
        get_array_parameter('area', request.query_params),
        rest_framework.CharFilter
    )

    if buildings:
        asset_handover_kwfilters[f'{handover_document_path}building__in'] = buildings
        location_matrix_package_kwfilters['package_handover_document__package_handover'
                                          '__package_matrix__locationmatrixpackage'
                                          '__location_matrix__building__in'] = buildings

    if levels:
        asset_handover_kwfilters[f'{handover_document_path}level__in'] = levels
        location_matrix_package_kwfilters['package_handover_document__package_handover'
                                          '__package_matrix__locationmatrixpackage'
                                          '__location_matrix__level__in'] = levels

    if areas:
        asset_handover_kwfilters[f'{handover_document_path}area__in'] = areas
        location_matrix_package_kwfilters['package_handover_document__package_handover'
                                          '__package_matrix__locationmatrixpackage'
                                          '__location_matrix__area__in'] = areas

    if any((buildings, levels, areas)):
        handover_document_filters.append(
            Q(
                Q(**asset_handover_kwfilters) |
                Q(Exists(PackageHandoverDocumentMedia.objects.filter(**location_matrix_package_kwfilters)),
                  **package_handover_kwfilters)
            )
        )


def extend_file_name_for_archive(name: str):
    name_path_parts = name.split('.')
    name_without_extension = '.'.join(name_path_parts[:-1])
    name_salt = str(uuid.uuid4())
    extension = name_path_parts[-1]

    return f'{name_without_extension}_{name_salt}.{extension}'


def replace_forward_slash_by_dash(source: str) -> str:
    return source.replace('/', '-')
