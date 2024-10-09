from typing import Optional

from django.db.models import F, Q

from api.models import PackageHandoverDocumentMedia, PackageHandoverDocument, Project, PackageHandoverStatistics, \
    PackageHandover, PackageHandoverDocumentMediaUpdate, User


class PackageHandoverStatisticsService:
    POSITIVE_MULTIPLIER = 1
    NEGATIVE_MULTIPLIER = -1

    def aggregate_status_counter_for_project(self, project: Project, user) -> dict:
        return PackageHandoverStatistics.objects.aggregate_status_counter_for_project(project.pk, user)

    def delete_on_package_handover_delete(self, package_handover: PackageHandover):
        package_handover_document_ids = list(package_handover.packagehandoverdocument_set.values_list('id', flat=True))
        PackageHandoverStatistics.objects.filter(
            package_handover_document_id__in=package_handover_document_ids,
        ).delete()

    def undelete_on_package_handover_undelete(self, package_handover: PackageHandover):
        package_handover_document_ids = list(package_handover.packagehandoverdocument_set.values_list('id', flat=True))
        PackageHandoverStatistics.deleted_objects.filter(
            package_handover_document_id__in=package_handover_document_ids,
        ).undelete()

    def create_on_package_handover_document_create(self, package_handover_document: PackageHandoverDocument) -> None:
        PackageHandoverStatistics.objects.create(
            package_handover_document_id=package_handover_document.id,
            project_id=package_handover_document.package_handover.package_matrix.project_id
        )

    def delete_on_package_handover_document_delete(self, package_handover_document: PackageHandoverDocument) -> None:
        PackageHandoverStatistics.objects.filter(
            package_handover_document_id=package_handover_document.id,
            project_id=package_handover_document.package_handover.package_matrix.project_id
        ).delete()

    def undelete_on_package_handover_document_undelete(self, package_handover_document: PackageHandoverDocument) -> None:
        PackageHandoverStatistics.objects.filter(
            package_handover_document_id=package_handover_document.id,
            project_id=package_handover_document.package_handover.package_matrix.project_id
        ).undelete()

    def decrease_for_package_handover_document_media_status(self, document_media: PackageHandoverDocumentMedia) -> None:
        self.__change_statistics_for_document_media_status(document_media, self.NEGATIVE_MULTIPLIER)

    def increase_for_package_handover_document_media_status(self, document_media: PackageHandoverDocumentMedia) -> None:
        self.__change_statistics_for_document_media_status(document_media, self.POSITIVE_MULTIPLIER)

    def update_statistics_by_statuses_on_package_handover_document_media_status_change(self, document_media: PackageHandoverDocumentMedia) -> None:
        queryset = PackageHandoverStatistics.objects.filter(
            package_handover_document_id=document_media.package_handover_document_id,
            company__isnull=True,
            group__isnull=True
        )

        if queryset.exists() and hasattr(document_media, 'update_fields_original_values'):
            old_status_count_field = '%s_count' % document_media.update_fields_original_values['status']
            new_status_count_field = '%s_count' % document_media.status

            queryset.update(**{
                old_status_count_field: F(old_status_count_field) - 1,
                new_status_count_field: F(new_status_count_field) + 1
            })

    def delete_on_project_delete(self, project: Project) -> None:
        PackageHandoverStatistics.objects.filter(project_id=project.id).delete()

    def change_on_package_handover_document_media_update(self, update: PackageHandoverDocumentMediaUpdate, user: User) -> None:
        def is_creation():
            return not update.old_data

        changed_status_count = {}

        if update.old_data.get('status') != update.new_data.get('status'):
            if 'status' in update.old_data:
                changed_status_count[f"{update.old_data['status']}_count"] = -1

            if 'status' in update.new_data:
                changed_status_count[f"{update.new_data['status']}_count"] = 1

        project_id = update.package_handover_document_media.package_handover_document.project_id
        package_handover_document_id = update.package_handover_document_media.package_handover_document_id

        # If it's not first update search for an initial update where media was uploaded or changed for the last time
        # to get company and group from a valid user.
        if not is_creation():
            initial_update = update.package_handover_document_media.packagehandoverdocumentmediaupdate_set.filter(
                Q(old_data={}) | ~Q(old_data__media=F('new_data__media'))
            ).order_by('-created_at').first()

            if initial_update:
                update = initial_update
            else:
                update = update.package_handover_document_media.packagehandoverdocumentmediaupdate_set.\
                    filter().order_by('created_at').first()

        package_handover_statistics_search_fields = {
            'package_handover_document_id': package_handover_document_id,
            'project_id': project_id,
            'group_id': user.group_id,
            'company_id': update.company_id
        }

        group_company_statistics = PackageHandoverStatistics.all_objects.filter(
            **package_handover_statistics_search_fields
        ).first()

        if is_creation() and group_company_statistics is None:
            PackageHandoverStatistics.objects.create(
                **package_handover_statistics_search_fields,
                **changed_status_count
            )
        else:
            self.__update_existing_group_company_statistics(group_company_statistics, changed_status_count)

    def __update_existing_group_company_statistics(
            self,
            group_company_statistics: Optional[PackageHandoverStatistics],
            changed_status_count: dict
    ) -> None:
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

    def __change_statistics_for_document_media_status(
            self,
            package_handover_document_media: PackageHandoverDocumentMedia,
            multiplier: int
    ) -> None:
        changing_field_name = '%s_count' % package_handover_document_media.status
        package_handover_document_id = int(package_handover_document_media.package_handover_document_id)
        filters = {
            'package_handover_document_id': package_handover_document_id
        }

        if multiplier > 0:
            filters.update(
                company__isnull=True,
                group__isnull=True,
            )
        elif multiplier < 0:
            filters[f'{changing_field_name}__gt'] = 0

        PackageHandoverStatistics.objects.filter(**filters).update(**{changing_field_name: F(changing_field_name) + multiplier})
