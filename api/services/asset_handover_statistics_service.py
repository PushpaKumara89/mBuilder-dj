from itertools import chain
from typing import Union

import pendulum
from django.db.models import Sum, Q, F
from django.db.models.functions import Coalesce
from django.utils.datastructures import MultiValueDict

from api.http.serializers.asset_handover.asset_handover_statistics.asset_handover_statistics_read_serializer import \
    AssetHandoverStatisticsReadSerializer
from api.models import User
from api.models.asset_handover.asset_handover import AssetHandover
from api.models.asset_handover.asset_handover_document import AssetHandoverDocument
from api.models.asset_handover.asset_handover_document_media import AssetHandoverDocumentMedia
from api.models.asset_handover.asset_handover_document_media_update import AssetHandoverDocumentMediaUpdate
from api.models.asset_handover.asset_handover_information import AssetHandoverInformation
from api.models.asset_handover.asset_handover_statistics import AssetHandoverStatistics
from api.models.package_matrix import PackageMatrix
from api.models.project import Project
from api.utilities.helpers import get_array_parameter, get_int_array_parameter


class AssetHandoverStatisticsService:
    POSITIVE_MULTIPLIER = 1
    NEGATIVE_MULTIPLIER = -1

    def aggregate_statistics_by_project(self, project, user=None):
        filters = {
            'project__pk': project.pk,
            'group__isnull': True,
            'company__isnull': True,
        }

        user_is_subcontractor = getattr(user, 'is_subcontractor', False)
        user_is_consultant = getattr(user, 'is_consultant', False)

        if user_is_subcontractor:
            filters['company_id'] = user.company_id
            filters['group__isnull'] = False
            del filters['company__isnull']
        elif user_is_consultant:
            filters['group__isnull'] = False
            del filters['company__isnull']

        aggregations_stumps = {}
        aggregations = {}

        for field in AssetHandoverStatisticsReadSerializer.Meta.fields:
            if user_is_consultant and field != 'accepted_count':
                aggregations_stumps[field] = 0
            else:
                aggregations[field] = Sum(field)

        aggregated_statistics = AssetHandoverStatistics.objects.filter(**filters).aggregate(**aggregations)
        aggregated_statistics['uploaded_files_count'] = self.__get_uploaded_files_count(aggregated_statistics)
        information_statistics = AssetHandoverInformation.objects.aggregate_statistics_by_project(project)
        aggregated_statistics = {**aggregated_statistics, **information_statistics}

        if user_is_consultant:
            aggregated_statistics.update(**aggregations_stumps)
            aggregated_statistics.update(**{key: 0 for key in information_statistics.keys()})

        return aggregated_statistics

    def aggregate_filtered_statistics_by_project(self, project, filters: Union[dict, MultiValueDict]) -> dict:
        filters = {
            'package_activity__packagematrix__deleted__isnull': True,
            'package_activity__packagematrix__package__in': get_int_array_parameter('package', filters),
            'package_activity__packagematrix__project': project,
            'location_matrix__building__in': get_array_parameter('building', filters),
            'location_matrix__level__in': get_array_parameter('level', filters),
            'location_matrix__area__in': get_array_parameter('area', filters),
            'package_activity_id__in': get_int_array_parameter('package_activity', filters),
            'project': project
        }
        filters = {filter_name: value for filter_name, value in filters.items() if value}

        information_statistics = AssetHandover.objects.filter(**filters).get_information_statistics()
        filters = {f'asset_handover_document__asset_handover__{filter_name}': filter_value for filter_name, filter_value in filters.items()}
        document_statistics = AssetHandoverStatistics.objects.\
            filter(**filters, group__isnull=True, company__isnull=True).\
            annotate(uploaded_files=F('in_progress_count') + F('contested_count') + F('accepted_count') + F('requesting_approval_count') + F('requested_approval_rejected_count')).\
            aggregate(
                required_files_count=Coalesce(Sum('required_files_count'), 0),
                uploaded_files_count=Coalesce(Sum('uploaded_files'), 0)
            )

        return {**information_statistics, **document_statistics}

    def create_on_asset_handover_document_create(self, asset_handover_document: AssetHandoverDocument) -> None:
        project_id = asset_handover_document.asset_handover.location_matrix.project_id
        AssetHandoverStatistics.objects.create(
            asset_handover_document_id=asset_handover_document.id,
            project_id=project_id,
            required_files_count=asset_handover_document.number_required_files,
        )

    def change_on_asset_handover_document_media_update(self, update: AssetHandoverDocumentMediaUpdate, user: User) -> None:
        def is_creation() -> bool:
            return not update.old_data

        changed_status_count = self.__fill_changed_status_count(update)
        project_id = update.asset_handover_document_media.asset_handover_document.asset_handover.project_id
        asset_handover_document_id = update.asset_handover_document_media.asset_handover_document_id
        required_files_count = update.asset_handover_document_media.asset_handover_document.number_required_files

        # If it's not first update search for an initial update where media was uploaded or changed for the last time
        # to get company and group from a valid user.
        if not is_creation():
            update = update.asset_handover_document_media.assethandoverdocumentmediaupdate_set.filter(
                Q(old_data={}) | ~Q(old_data__media=F('new_data__media'))
            ).order_by('-created_at').first()

        asset_handover_statistics_search_fields = {
            'asset_handover_document_id': asset_handover_document_id,
            'project_id': project_id,
            'required_files_count': required_files_count,
            'group_id': user.group_id,
            'company_id': update.company_id
        }

        group_company_statistics = AssetHandoverStatistics.all_objects.filter(
            **asset_handover_statistics_search_fields
        ).first()

        if is_creation() and group_company_statistics is None:
            AssetHandoverStatistics.objects.create(
                **asset_handover_statistics_search_fields,
                **changed_status_count
            )
        else:
            self.__update_existing_group_company_statistics(group_company_statistics, changed_status_count)

    def __fill_changed_status_count(self, update: AssetHandoverDocumentMediaUpdate) -> dict:
        changed_status_count = {}

        if update.old_data.get('status') != update.new_data.get('status'):
            if 'status' in update.old_data:
                changed_status_count[f"{update.old_data['status']}_count"] = -1

            if 'status' in update.new_data:
                changed_status_count[f"{update.new_data['status']}_count"] = 1

        return changed_status_count

    def __update_existing_group_company_statistics(self, group_company_statistics: AssetHandoverStatistics, changed_status_count: dict) -> None:
        if group_company_statistics:
            changed_fields = []

            if changed_status_count:
                changed_fields.extend(changed_status_count.keys())

            for field, value in changed_status_count.items():
                setattr(group_company_statistics, field, getattr(group_company_statistics, field) + value)

            if group_company_statistics.deleted:
                group_company_statistics.deleted = None
                changed_fields.append('deleted')

            if changed_fields:
                group_company_statistics.save(update_fields=changed_fields)

    def update_on_asset_handover_document_update(self, asset_handover_document: AssetHandoverDocument) -> None:
        diff = asset_handover_document.number_required_files - asset_handover_document.update_fields_original_values['number_required_files']

        if diff:
            AssetHandoverStatistics.objects.update_on_asset_handover_document_change(
                diff=diff,
                asset_handover_document_id=asset_handover_document.id
            )

    def decrease_for_asset_handover_document_media_status(self, document_media: AssetHandoverDocumentMedia) -> None:
        AssetHandoverStatistics.objects.change_statistics_for_document_status(
            document_media, self.NEGATIVE_MULTIPLIER
        )

    def increase_for_asset_handover_document_media_status(self, document_media: AssetHandoverDocumentMedia) -> None:
        AssetHandoverStatistics.objects.change_statistics_for_document_status(
            document_media, self.POSITIVE_MULTIPLIER
        )

    def update_statistics_by_statuses_on_asset_handover_document_media_status_change(self, document_media: AssetHandoverDocumentMedia) -> None:
        AssetHandoverStatistics.objects.update_on_asset_handover_document_media_status_change(document_media)

    def delete_on_asset_handover_delete(self, asset_handover: AssetHandover) -> None:
        AssetHandoverStatistics.objects.filter(
            asset_handover_document_id__in=asset_handover.assethandoverdocument_set.values_list('id', flat=True),
        ).update(deleted=pendulum.now())

    def undelete_on_asset_handover_undelete(self, asset_handovers: list[AssetHandover]) -> None:
        asset_handover_documents = list(chain.from_iterable([
            list(asset_handover.assethandoverdocument_set.values_list('id', flat=True))
            for asset_handover in asset_handovers
        ]))

        AssetHandoverStatistics.deleted_objects.filter(
            asset_handover_document_id__in=asset_handover_documents,
        ).undelete()

    def delete_on_package_matrix_delete(self, package_matrix: PackageMatrix) -> None:
        package_activity_id = package_matrix.package_activity_id
        project_id = package_matrix.project_id

        asset_handovers = AssetHandover.objects.prefetch_related('assethandoverdocument_set').filter(
            location_matrix__project_id=project_id,
            package_activity_id=package_activity_id
        ).all()

        AssetHandoverStatistics.objects.filter(
            asset_handover_document_id__in=asset_handovers.values_list('assethandoverdocument__id', flat=True)
        ).delete()

    def undelete_on_package_matrix_undelete(self, package_matrix: PackageMatrix) -> None:
        package_activity_id = package_matrix.package_activity_id
        project_id = package_matrix.project_id

        asset_handovers = AssetHandover.deleted_objects.get_for_project_package_activity(
            project_id=project_id, package_activity_id=package_activity_id
        )

        AssetHandoverStatistics.deleted_objects.filter(
            asset_handover_document_id__in=asset_handovers.values_list('assethandoverdocument__id', flat=True)
        ).update(deleted=None)

    def delete_on_project_delete(self, project: Project) -> None:
        AssetHandoverStatistics.objects.filter(project_id=project.id).delete()

    def __get_uploaded_files_count(self, aggregated_statistics: dict):
        return sum([0 if value is None else value
                    for field_name, value in aggregated_statistics.items()
                    if field_name != 'required_files_count'])
