from django.urls import include, path, re_path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_mongoengine.routers import DefaultRouter as MongoEngineDefaultRouter

from api.http.views import UserViewSet, LogoutView, ProfileViewSet, PackageViewSet, PackageActivityViewSet, \
    PackageActivityTaskViewSet, EditModeViewSet, RecipientViewSet, LocationMatrixViewSet, \
    MediaViewSet, PackageMatrixViewSet, ProjectNewsViewSet, ProjectViewSet, SubtaskUpdateViewSet, \
    TaskUpdateViewSet, TaskViewSet, SubtaskViewSet, LocationMatrixPackagesViewSet, TaskUpdateRecipientView, \
    CompanyViewSet, SubtaskUpdateRecipientView, HealthCheckView, QualityIssueViewSet, \
    QualityIssueUpdateViewSet, PackageMatrixActivityViewSet, CommandViewSet, PackageHandoverDocumentGroupViewSet, \
    PackageHandoverDocumentTypeViewSet, PackageHandoverDocumentViewSet, PackageHandoverDocumentMediaViewSet, \
    PackageHandoverViewSet, PackageHandoverDocumentMediaUpdateViewSet, PackageHandoverDocumentMediaUpdateBulkViewSet, \
    PackageHandoverDocumentMediaBulkViewSet, ResponseCategoryViewSet, AssetHandoverDocumentTypeViewSet, \
    AssetHandoverViewSet, AssetHandoverDocumentViewSet, AssetHandoverInformationViewSet, \
    AssetHandoverDocumentMediaViewSet, FloorPlanViewSet, AssetHandoverCompanyViewSet, PackageHandoverCompanyViewSet, AppSettingsViewSet
from api.http.views.api_key_view_set import ApiKeyViewSet
from api.http.views.asset_handover.asset_handover_document_media_update_bulk_view_set import \
    AssetHandoverDocumentMediaUpdateBulkViewSet
from api.http.views.asset_handover.asset_handover_document_media_update_view_set import \
    AssetHandoverDocumentMediaUpdateViewSet
from api.http.views.asset_handover.asset_handover_statistics_by_project_view_set import \
    AssetHandoverStatisticsByProjectViewSet
from api.http.views.asset_register_view_set import AssetRegisterViewSet
from api.http.views.event_view_set import EventViewSet
from api.http.views.floor_plan.floor_plan_quality_issue_view_set import FloorPlanQualityIssueViewSet
from api.http.views.floor_plan.floor_plan_subtask_view_set import FloorPlanSubtaskViewSet
from api.http.views.floor_plan_area_pin.floor_plan_area_quality_issue_pin_view_set import \
    FloorPlanAreaQualityIssuePinViewSet
from api.http.views.floor_plan_area_pin.floor_plan_area_subtask_pin_view_set import FloorPlanAreaSubtaskPinViewSet
from api.http.views.floor_plan_area_pin_thumbnail.floor_plan_area_pin_thumbnail_view_set import \
    FloorPlanAreaPinThumbnailViewSet
from api.http.views.floor_plan_areas.floor_plan_area_bulk_view_set import FloorPlanAreaBulkViewSet
from api.http.views.floor_plan_areas.floor_plan_area_view_set import FloorPlanAreaViewSet
from api.http.views.floor_plan_level_view_set import FloorPlanLevelViewSet
from api.http.views.floor_plan_building_view_set import FloorPlanBuildingViewSet
from api.http.views.floor_plan_package_view_set import FloorPlanPackageViewSet
from api.http.views.floor_plan_revisions_view_set import FloorPlanRevisionViewSet
from api.http.views.handover_document.handover_document_media_batch_download_view_set import HandoverDocumentMediaBatchDownloadViewSet
from api.http.views.handover_document.handover_document_view_set import HandoverDocumentViewSet
from api.http.views.handover_document.handover_documents_company_view_set import HandoverDocumentsCompanyViewSet
from api.http.views.locations.locations_area_view import LocationsAreaView
from api.http.views.locations.locations_building_view import LocationsBuildingView
from api.http.views.locations.locations_level_view import LocationsLevelView
from api.http.views.package_handover.package_handover_statistics_view_set import PackageHandoverStatisticsViewSet
from api.http.views.package_matrix_company_view_set import PackageMatrixCompanyViewSet
from api.http.views.project_snapshot_view_set import ProjectSnapshotViewSet
from api.http.views.quality_issue_bulk_create_view_set import QualityIssueBulkCreateViewSet

router = routers.DefaultRouter()
mongo_router = MongoEngineDefaultRouter()

package_list = PackageViewSet.as_view({
    'get': 'list',
    'post': 'create',
    'put': 'sync'
})

package_detail = PackageViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

location_matrix_list = LocationMatrixViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

location_matrix_detail = LocationMatrixViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'delete': 'destroy',
    'patch': 'partial_update'
})

location_matrix_packages_list = LocationMatrixPackagesViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

location_matrix_packages_detail = LocationMatrixPackagesViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'delete': 'destroy',
    'patch': 'partial_update'
})

tasks_list = TaskViewSet.as_view({
    'get': 'list',
})

tasks_detail = TaskViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update'
})

tasks_updates_detail = TaskUpdateViewSet.as_view({
    'get': 'retrieve',
    'delete': 'destroy'
})

tasks_updates_list = TaskUpdateViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

quality_issue_updates_detail = QualityIssueUpdateViewSet.as_view({
    'get': 'retrieve',
    'delete': 'destroy'
})

quality_issue_updates_list = QualityIssueUpdateViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

subtasks_updates_detail = SubtaskUpdateViewSet.as_view({
    'get': 'retrieve',
    'delete': 'destroy'
})

subtasks_updates_list = SubtaskUpdateViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

subtasks_detail = SubtaskViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

subtasks_list = SubtaskViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

quality_issue_detail = QualityIssueViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

quality_issue_list = QualityIssueViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

recipient_detail = RecipientViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

package_matrix_companies_details = PackageMatrixCompanyViewSet.as_view({
    'delete': 'destroy'
})

package_matrix_companies_list = PackageMatrixCompanyViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

package_handovers_list = PackageHandoverViewSet.as_view({
    'get': 'list',
})

package_handovers_detail = PackageHandoverViewSet.as_view({
    'put': 'update',
})

package_handover_documents_list = PackageHandoverDocumentViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

package_handover_documents_detail = PackageHandoverDocumentViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

package_handover_document_media_list = PackageHandoverDocumentMediaViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

package_handover_document_media_detail = PackageHandoverDocumentMediaViewSet.as_view({
    'get': 'retrieve',
    'delete': 'destroy'
})

package_handover_document_media_updates_list = PackageHandoverDocumentMediaUpdateViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

package_handover_document_media_updates_detail = PackageHandoverDocumentMediaUpdateViewSet.as_view({
    'get': 'retrieve',
})

response_category_list = ResponseCategoryViewSet.as_view({
    'post': 'create',
    'get': 'list'
})

response_category_detail = ResponseCategoryViewSet.as_view({
    'put': 'update',
    'delete': 'destroy',
    'get': 'retrieve'
})

asset_handover_document_list = AssetHandoverDocumentViewSet.as_view({
    'post': 'create',
    'get': 'list'
})

asset_handover_document_detail = AssetHandoverDocumentViewSet.as_view({
    'delete': 'destroy',
})

asset_handover_document_media_list = AssetHandoverDocumentMediaViewSet.as_view({
    'post': 'create',
    'get': 'list'
})

asset_handover_document_media_detail = AssetHandoverDocumentMediaViewSet.as_view({
    'delete': 'destroy',
    'get': 'retrieve'
})

floor_plan_list = FloorPlanViewSet.as_view({
    'post': 'create',
    'get': 'list'
})

floor_plan_detail = FloorPlanViewSet.as_view({
    'put': 'update',
    'delete': 'destroy',
    'get': 'retrieve'
})

asset_handover_document_media_update_list = AssetHandoverDocumentMediaUpdateViewSet.as_view({
    'post': 'create',
    'get': 'list'
})

asset_handover_document_media_update_detail = AssetHandoverDocumentMediaUpdateViewSet.as_view({
    'get': 'retrieve',
})

asset_handover_information_list = AssetHandoverInformationViewSet.as_view({
    'post': 'create',
    'get': 'list'
})

asset_handover_information_detail = AssetHandoverInformationViewSet.as_view({
    'put': 'update',
    'get': 'retrieve'
})

asset_register_list = AssetRegisterViewSet.as_view({
    'put': 'update',
    'get': 'retrieve',
    'delete': 'destroy',
    'post': 'create'
})

floor_plan_area_list = FloorPlanAreaViewSet.as_view({
    'get': 'list',
    'post': 'create'
})

floor_plan_area_detail = FloorPlanAreaViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'delete': 'destroy',
})

floor_plan_area_subtask_pin_list = FloorPlanAreaSubtaskPinViewSet.as_view({
    'get': 'list'
})

floor_plan_area_quality_issue_pin_list = FloorPlanAreaQualityIssuePinViewSet.as_view({
    'get': 'list'
})

floor_plan_subtask_list = FloorPlanSubtaskViewSet.as_view({
    'get': 'list'
})

floor_plan_quality_issue_list = FloorPlanQualityIssueViewSet.as_view({
    'get': 'list'
})

floor_plan_area_pin_thumbnail_list = FloorPlanAreaPinThumbnailViewSet.as_view({
    'post': 'create'
})

router.register(r'package-handover-document-groups', PackageHandoverDocumentGroupViewSet, basename='package_handover_document_groups')
router.register(r'package-handover-document-types', PackageHandoverDocumentTypeViewSet, basename='package_handover_document_types')
router.register(r'asset-handover-document-types', AssetHandoverDocumentTypeViewSet, basename='asset_handover_document_types')
router.register(r'package-activity-tasks', PackageActivityTaskViewSet, basename='package_activity_tasks')
router.register(r'package-activities', PackageActivityViewSet, basename='package_activities')
router.register(r'project-news', ProjectNewsViewSet, basename='project-news')
router.register(r'companies', CompanyViewSet, basename='companies')
router.register(r'projects', ProjectViewSet, basename='projects')
router.register(r'api-keys', ApiKeyViewSet, basename='api_keys')
router.register(r'media', MediaViewSet, basename='media')
router.register(r'users', UserViewSet, basename='users')
router.register(r'', ProfileViewSet, basename='profile')

urlpatterns = [
    path('projects/<int:project_pk>/floor-plans/<int:pk>/temporary-pin-thumbnails/', floor_plan_area_pin_thumbnail_list, name='floor_plan_area_pin_thumbnail-list'),

    path('projects/<int:project_pk>/subtasks/floor-plan-area-pins/', floor_plan_area_subtask_pin_list, name='floor_plan_area_subtask-list'),
    path('projects/<int:project_pk>/quality-issues/floor-plan-area-pins/', floor_plan_area_quality_issue_pin_list, name='floor_plan_area_quality_issue-list'),

    path('projects/<int:project_pk>/subtasks/floor-plans/', floor_plan_subtask_list, name='floor_plan_subtask-list'),
    path('projects/<int:project_pk>/quality-issues/floor-plans/', floor_plan_quality_issue_list, name='floor_plan_quality_issue-list'),

    path('projects/<int:project_pk>/floor-plans/floor_plan_revisions/', FloorPlanRevisionViewSet.as_view({'get': 'list'}), name='floor_plan_revisions-list'),
    path('projects/<int:project_pk>/floor-plans/floor_plan_revisions/<int:pk>/', FloorPlanRevisionViewSet.as_view({'get': 'retrieve'}), name='floor_plan_revisions-retrieve'),
    path('projects/<int:project_pk>/floor-plans/<int:floor_plan_pk>/floor_plan_revisions/<int:pk>/revert/', FloorPlanRevisionViewSet.as_view({'post': 'revert'}), name='floor_plan_revisions-revert'),

    path('projects/<int:project_pk>/asset-register/', asset_register_list, name='asset_register-list'),
    path('app-settings/', AppSettingsViewSet.as_view({'get': 'retrieve', 'put': 'update'}), name='app-settings'),
    path('projects/<int:project_pk>/handover-documents/companies/', HandoverDocumentsCompanyViewSet.as_view({'get': 'list'}), name='handover_document-companies'),
    path('handover-documents/package-activities/', PackageActivityViewSet.as_view({'get': 'list_for_handover_documents'}), name='handover_document-package_activities-list'),

    path('projects/<int:project_pk>/handover-documents/<int:pk>/', HandoverDocumentViewSet.as_view({'get': 'retrieve'}), name='handover_documents-retrieve'),
    path('projects/<int:project_pk>/handover-documents/csv/', HandoverDocumentViewSet.as_view({'get': 'generate_csv'}), name='handover_documents-generate_csv'),
    path('projects/<int:project_pk>/handover-documents/archive/', HandoverDocumentViewSet.as_view({'get': 'get_archive'}), name='handover_documents-generate_archive'),
    path('projects/<int:project_pk>/handover-documents/', HandoverDocumentViewSet.as_view({'get': 'list'}), name='handover_documents-list'),
    path('projects/<int:project_pk>/handover-documents/<int:pk>/media/', MediaViewSet.as_view({'get': 'retrieve_handover_document_media'}), name='handover_documents-media'),
    path('projects/<int:project_pk>/handover-documents/media/batch/', HandoverDocumentMediaBatchDownloadViewSet.as_view({'post': 'download'}), name='handover_documents-media_batch'),

    path('projects/<int:project_pk>/package-handovers/companies/', PackageHandoverCompanyViewSet.as_view({'get': 'list'}), name='package_handover_companies-list'),

    path('projects/<int:project_pk>/asset-handover-information/', asset_handover_information_list, name='asset_handover_information_list'),
    path('projects/<int:project_pk>/asset-handover-information/<int:pk>/', asset_handover_information_detail, name='asset_handover_information_detail'),

    path('projects/<int:project_pk>/asset-handover-document-media/<int:media_pk>/updates/', asset_handover_document_media_update_list, name='asset_handover_document_media_update_list'),
    path('projects/<int:project_pk>/asset-handover-document-media/<int:media_pk>/updates/<int:pk>/', asset_handover_document_media_update_detail, name='asset_handover_document_media_update_detail'),

    path('projects/<int:project_pk>/asset-handover-document-media/<int:pk>/download/', MediaViewSet.as_view({'get': 'retrieve_asset_handover_document_media'}), name='asset_handover_document_media_download'),

    path('projects/<int:project_pk>/package-matrix/activities/', PackageMatrixActivityViewSet.as_view({'get': 'list'}), name='package_matrix-activity_list'),
    path('projects/<int:project_pk>/package-handover-document-types/', PackageHandoverDocumentTypeViewSet.as_view({'get': 'get_for_project'}), name='project_package_handover_document_types'),

    path('projects/<int:project_pk>/floor-plans/', floor_plan_list, name='floor_plan_list'),
    path('projects/<int:project_pk>/floor-plans/<int:pk>/', floor_plan_detail, name='floor_plan_detail'),

    path('projects/<int:project_pk>/floor-plans/buildings/', FloorPlanBuildingViewSet.as_view({'get': 'list'}), name='floor_plan_building_list'),
    path('projects/<int:project_pk>/floor-plans/level/', FloorPlanLevelViewSet.as_view({'get': 'list'}), name='floor_plan_level_list'),
    path('projects/<int:project_pk>/floor-plans/packages/', FloorPlanPackageViewSet.as_view({'get': 'list'}), name='floor_plan_package_list'),

    path('projects/<int:project_pk>/floor-plan-areas/', floor_plan_area_list, name='floor_plan_area_list'),
    path('projects/<int:project_pk>/floor-plan-areas/bulk/', FloorPlanAreaBulkViewSet.as_view({'post': 'perform_actions'}), name='floor_plan_area_bulk'),
    path('projects/<int:project_pk>/floor-plan-areas/<int:pk>/', floor_plan_area_detail, name='floor_plan_area_detail'),

    path('projects/<int:project_pk>/asset-handover-documents/', asset_handover_document_list, name='asset_handover_document_list'),
    path('projects/<int:project_pk>/asset-handovers/', AssetHandoverViewSet.as_view({'get': 'list', 'post': 'create'}), name='asset_handover_list'),
    path('projects/<int:project_pk>/asset-handovers/information-csv/', AssetHandoverDocumentMediaViewSet.as_view({'get': 'generate_handover_information_csv'}), name='asset_handovers_generate_information_csv'),
    path('projects/<int:project_pk>/asset-handovers/companies/', AssetHandoverCompanyViewSet.as_view({'get': 'list'}), name='asset_handover_company_list'),
    path('projects/<int:project_pk>/asset-handovers/csv/', AssetHandoverViewSet.as_view({'get': 'generate_csv'}), name='asset_handover_generate_csv'),
    path('projects/<int:project_pk>/asset-handovers/<int:pk>/', AssetHandoverViewSet.as_view({'delete': 'destroy', 'put': 'update'}), name='asset_handover_details'),
    path('projects/<int:project_pk>/asset-handover-documents/<int:pk>/', asset_handover_document_detail, name='asset_handover_document_detail'),
    path('projects/<int:project_pk>/asset-handover-documents/<int:pk>/media-updates/bulk/', AssetHandoverDocumentMediaUpdateBulkViewSet.as_view({'post': 'create'}), name='bulk_create_asset_handover_document_media_updates'),

    path('projects/<int:project_pk>/asset-handover-document-media/', asset_handover_document_media_list, name='asset_handover_document_media_list'),
    path('projects/<int:project_pk>/asset-handover-document-media/bulk/', AssetHandoverDocumentMediaViewSet.as_view({'post': 'bulk_create'}), name='asset_handover_document_media_bulk_create'),
    path('projects/<int:project_pk>/asset-handover-document-media/batch/', AssetHandoverDocumentMediaViewSet.as_view({'post': 'batch_download'}), name='asset_handover_document_media_batch'),
    path('projects/<int:project_pk>/asset-handover-statistics/project/', AssetHandoverStatisticsByProjectViewSet.as_view({'get': 'get_project_statistics'}), name='asset_handover_project_statistics'),
    path('projects/<int:project_pk>/asset-handover-statistics/', AssetHandoverStatisticsByProjectViewSet.as_view({'get': 'get_filtered_project_statistics'}), name='asset_handover_statistics-filtered'),
    path('projects/<int:project_pk>/asset-handover-document-media/<int:pk>/', asset_handover_document_media_detail, name='asset_handover_document_media_detail'),

    path('media/bulk-create/', MediaViewSet.as_view({'post': 'bulk_create'}), name='media_bulk_create'),

    path('projects/<int:pk>/events/', EventViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('projects/<int:pk>/commands/', CommandViewSet.as_view({'post': 'create', 'get': 'list'})),
    path('projects/<int:pk>/snapshot/', ProjectSnapshotViewSet.as_view({'get': 'retrieve'})),

    path('projects/csv/', ProjectViewSet.as_view({'get': 'generate_csv'}), name='project_generate_csv'),

    path('logout/', LogoutView.as_view(), name='api_logout'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('companies/csv/', CompanyViewSet.as_view({'get': 'generate_csv'}), name='company_generate_csv'),

    path('packages/csv/', PackageViewSet.as_view({'get': 'generate_csv'}), name='package_generate_csv'),
    path('packages/<int:pk>/', package_detail, name='packages_detail'),
    path('packages/', package_list, name='packages_list'),

    path('package-activities/csv/', PackageActivityViewSet.as_view({'get': 'generate_csv'}), name='package_activities_generate_csv'),

    path('package-matrix/<int:pk>/', PackageMatrixViewSet.as_view({'delete': 'destroy'}), name='package_matrix_destroy'),

    path('projects/<int:project_pk>/users/<int:user_pk>/', ProjectViewSet.as_view({'put': 'update_user'}), name='project_users_update_user'),

    path('projects/<int:project_pk>/package-matrix/csv/', PackageMatrixViewSet.as_view({'get': 'generate_csv'}), name='package_matrix_generate_csv'),
    path('projects/<int:project_pk>/package-matrix/', PackageMatrixViewSet.as_view({'get': 'list', 'post': 'create'}), name='package_matrix_list'),
    path('projects/<int:project_pk>/package-matrix/packages/', PackageViewSet.as_view({'get': 'matrix_packages'}), name='package_matrix_packages-list'),

    path('projects/<int:project_pk>/package-matrix/<int:package_matrix_pk>/activity-tasks/<int:task_pk>/hide/', PackageActivityTaskViewSet.as_view({'post': 'hide'}), name='hide_package_activity_task'),
    path('projects/<int:project_pk>/package-matrix/<int:package_matrix_pk>/activity-tasks/<int:task_pk>/show/', PackageActivityTaskViewSet.as_view({'post': 'show'}), name='show_package_activity_task'),

    path('projects/<int:project_pk>/package-matrix-companies/', package_matrix_companies_list, name='package_matrix_companies_list'),
    path('projects/<int:project_pk>/package-matrix-companies/<int:pk>/', package_matrix_companies_details, name='package_matrix_companies_details'),

    path('projects/<int:project_pk>/package-activities/<int:package_activity_pk>/', PackageActivityViewSet.as_view({'get': 'get_for_matrix'}), name='matrix_package_activity_list'),
    path('projects/<int:project_pk>/asset-handovers/bulk-delete/', AssetHandoverViewSet.as_view({'delete': 'bulk_destroy'}), name='asset_handover_bulk_destroy'),

    path('projects/<int:project_pk>/location-matrix-packages/<int:pk>/', location_matrix_packages_detail, name='location_matrix_packages_detail'),
    path('projects/<int:project_pk>/location-matrix-packages/csv/', LocationMatrixPackagesViewSet.as_view({'get': 'generate_csv'}), name='location_matrix_packages_generate_csv'),
    path('projects/<int:project_pk>/location-matrix-packages/sync/', LocationMatrixPackagesViewSet.as_view({'put': 'sync'}), name='location_matrix_packages_sync'),
    path('projects/<int:project_pk>/location-matrix-packages/', location_matrix_packages_list, name='location_matrix_packages_list'),
    path('projects/<int:project_pk>/location-matrix-packages/<int:pk>/media/add/', LocationMatrixPackagesViewSet.as_view({'post': 'add_media'}), name='location_matrix_packages_add_media'),
    path('projects/<int:project_pk>/location-matrix-packages/<int:pk>/media/remove/', LocationMatrixPackagesViewSet.as_view({'post': 'remove_media'}), name='location_matrix_packages_remove_media'),

    path('projects/<int:project_pk>/location-matrix/sync/', LocationMatrixViewSet.as_view({'post': 'sync'}), name='location_matrix_bulk_create'),
    path('projects/<int:project_pk>/location-matrix/csv/', LocationMatrixViewSet.as_view({'get': 'generate_csv'}), name='location_matrix_generate_csv'),
    path('projects/<int:project_pk>/location-matrix/qr-codes/', LocationMatrixViewSet.as_view({'get': 'qr_codes'}), name='location_matrix_get_qr_codes'),
    path('projects/<int:project_pk>/location-matrix/', location_matrix_list, name='location_matrix_list'),
    path('location-matrix/<int:pk>/', location_matrix_detail, name='location_matrix_detail'),

    path('projects/<int:project_pk>/tasks/updates/', TaskUpdateViewSet.as_view({'post': 'bulk_create'}), name='bulk_create_tasks_updates'),
    path('projects/<int:project_pk>/tasks/<int:pk>/', tasks_detail, name='tasks_detail'),
    path('projects/<int:project_pk>/tasks/<int:task_pk>/updates/<int:pk>/', tasks_updates_detail, name='tasks_updates_detail'),
    path('projects/<int:project_pk>/tasks/<int:task_pk>/updates/', tasks_updates_list, name='tasks_updates_list'),
    path('projects/<int:project_pk>/tasks/', tasks_list, name='tasks_list'),
    path('projects/<int:project_pk>/tasks/assigned-users/', TaskViewSet.as_view({'get': 'assigned_users'}), name='tasks_assigned_users'),
    path('projects/<int:project_pk>/tasks/csv/', TaskViewSet.as_view({'get': 'generate_csv'}), name='tasks_generate_csv'),
    path('projects/<int:project_pk>/tasks/client-csv/', TaskViewSet.as_view({'get': 'generate_client_csv'}), name='tasks_generate_client_csv'),
    path('projects/<int:project_pk>/tasks/pdf/', TaskViewSet.as_view({'get': 'generate_pdf'}), name='tasks_generate_pdf'),
    path('projects/<int:project_pk>/tasks/client-pdf/', TaskViewSet.as_view({'get': 'generate_client_pdf'}), name='tasks_generate_client_pdf'),

    path('projects/<int:project_pk>/subtasks/<int:subtask_pk>/updates/<int:pk>/', subtasks_updates_detail, name='subtasks_updates_detail'),
    path('projects/<int:project_pk>/subtasks/<int:subtask_pk>/updates/', subtasks_updates_list, name='subtasks_updates_list'),
    path('projects/<int:project_pk>/subtasks/<int:pk>/', subtasks_detail, name='subtasks_detail'),
    path('projects/<int:project_pk>/subtasks/', subtasks_list, name='subtasks_list'),
    path('projects/<int:project_pk>/subtasks/bulk/', SubtaskViewSet.as_view({'post': 'bulk_create_from_tasks'}), name='subtasks_bulk_create'),
    path('projects/<int:project_pk>/quality-issues/subtasks/bulk/', SubtaskViewSet.as_view({'post': 'bulk_create_from_quality_issues'}), name='subtasks_bulk_create_from_quality_issues'),
    path('projects/<int:project_pk>/subtasks/creators/', SubtaskViewSet.as_view({'get': 'creators'}), name='subtasks_creators'),
    path('projects/<int:project_pk>/subtasks/companies/', SubtaskViewSet.as_view({'get': 'companies'}), name='subtasks_companies'),
    path('projects/<int:project_pk>/subtasks/count/', SubtaskViewSet.as_view({'get': 'count'}), name='subtasks_count'),
    path('projects/<int:project_pk>/subtasks/<int:pk>/files/', SubtaskViewSet.as_view({'get': 'retrieve_files'}), name='subtasks_files'),
    path('projects/<int:project_pk>/subtasks/<int:pk>/files/add/', SubtaskViewSet.as_view({'post': 'add_files'}), name='subtasks_add_files'),
    path('projects/<int:project_pk>/subtasks/<int:pk>/files/remove/', SubtaskViewSet.as_view({'post': 'remove_files'}), name='subtasks_add_files'),
    path('projects/<int:project_pk>/subtasks/csv/', SubtaskViewSet.as_view({'get': 'generate_csv'}), name='subtasks_generate_csv'),
    path('projects/<int:project_pk>/subtasks/pdf/', SubtaskViewSet.as_view({'get': 'generate_pdf'}), name='subtasks_generate_pdf'),

    path('projects/<int:project_pk>/locations/buildings/', LocationsBuildingView.as_view({'get': 'list'}), name='locations_buildings'),
    path('projects/<int:project_pk>/locations/levels/', LocationsLevelView.as_view({'get': 'list'}), name='locations_levels'),
    path('projects/<int:project_pk>/locations/areas/', LocationsAreaView.as_view({'get': 'list'}), name='locations_areas'),

    path('projects/<int:project_pk>/edit-mode/', EditModeViewSet.as_view({'delete': 'destroy', 'post': 'create', 'get': 'retrieve'}), name='edit_mode_list'),

    path('users/<str:email>/restore/', UserViewSet.as_view({'post': 'restore'}), name='restore_user'),

    path('recipients/', RecipientViewSet.as_view({'post': 'create'}), name='recipients_create'),
    path('recipients/<int:pk>/', recipient_detail, name='recipient_detail'),
    path('projects/<int:project_pk>/recipients/', RecipientViewSet.as_view({'get': 'list'}), name='recipients_search'),
    path('projects/<int:project_pk>/task-update/recipients/', TaskUpdateRecipientView.as_view({'get': 'list'}), name='task_update_recipients_search'),
    path('projects/<int:project_pk>/subtask-update/recipients/', SubtaskUpdateRecipientView.as_view({'get': 'list'}), name='subtask_update_recipients_search'),

    path('projects/<int:project_pk>/quality-issues/', quality_issue_list, name='quality_issue_list'),
    path('projects/<int:project_pk>/quality-issues/<int:pk>/', quality_issue_detail, name='quality_issue_detail'),
    path('projects/<int:project_pk>/quality-issues/bulk/', QualityIssueBulkCreateViewSet.as_view({'post': 'bulk_create'}), name='quality_issue-bulk_create'),
    path('projects/<int:project_pk>/quality-issues/creators/', QualityIssueViewSet.as_view({'get': 'creators'}), name='quality_issue_creators'),
    path('projects/<int:project_pk>/quality-issues/count/', QualityIssueViewSet.as_view({'get': 'count'}), name='quaity_issue_count'),
    path('projects/<int:project_pk>/quality-issues/pdf/', QualityIssueViewSet.as_view({'get': 'generate_pdf'}), name='quaity_issue_generate_pdf'),
    path('projects/<int:project_pk>/quality-issues/csv/', QualityIssueViewSet.as_view({'get': 'generate_csv'}), name='quaity_issue_generate_csv'),

    path('projects/<int:project_pk>/quality-issues/<int:quality_issue_pk>/updates/', quality_issue_updates_list, name='quality_issue_update_list'),
    path('projects/<int:project_pk>/quality-issues/<int:quality_issue_pk>/updates/<int:pk>/', quality_issue_updates_detail, name='quality_issue_update_detail'),

    path('projects/<int:project_pk>/package-handovers/', PackageHandoverDocumentViewSet.as_view({'get': 'list_grouped'}), name='package_handover_documents_list_grouped'),
    path('projects/<int:project_pk>/package-handovers/csv/', PackageHandoverViewSet.as_view({'get': 'generate_csv'}), name='package_handovers_generate_csv'),
    path('projects/<int:project_pk>/package-handovers/information-csv/', PackageHandoverDocumentMediaViewSet.as_view({'get': 'generate_handover_information_csv'}), name='package_handovers_generate_information_csv'),
    path('projects/<int:project_pk>/package-handovers/<int:pk>/', package_handovers_detail, name='package_handovers_detail'),
    path('projects/<int:project_pk>/package-handovers-statistics/status-counter/', PackageHandoverStatisticsViewSet.as_view({'get': 'get_status_counter'}), name='package_handovers_statistics-project_status_counter'),

    path('projects/<int:project_pk>/package-handover-documents/', package_handover_documents_list, name='package_handover_documents_list'),
    path('projects/<int:project_pk>/package-handover-documents/<int:pk>/', package_handover_documents_detail, name='package_handover_documents_detail'),

    path('projects/<int:project_pk>/package-handover-document-media/', package_handover_document_media_list, name='package_handover_document_media_list'),
    path('projects/<int:project_pk>/package-handover-document-media/bulk/', PackageHandoverDocumentMediaBulkViewSet.as_view({'post': 'create'}), name='bulk_create_package_handover_document_media'),
    path('projects/<int:project_pk>/package-handover-document-media/batch/', PackageHandoverDocumentMediaViewSet.as_view({'post': 'batch_download'}), name='package_handover_document_media_batch'),
    path('projects/<int:project_pk>/package-handover-document-media/<int:pk>/', package_handover_document_media_detail, name='package_handover_document_media_detail'),
    path('projects/<int:project_pk>/package-handover-document-media/<int:pk>/download/', MediaViewSet.as_view({'get': 'retrieve_package_handover_document_media'}), name='package_handover_document_media_download'),

    path('projects/<int:project_pk>/package-handover-documents/<int:pk>/media-updates/bulk/', PackageHandoverDocumentMediaUpdateBulkViewSet.as_view({'post': 'create'}), name='bulk_create_package_handover_document_media_updates'),
    path('projects/<int:project_pk>/package-handover-document-media/<int:media_pk>/updates/', package_handover_document_media_updates_list, name='package_handover_document_media_updates_list'),
    path('projects/<int:project_pk>/package-handover-document-media/<int:media_pk>/updates/<int:pk>/', package_handover_document_media_updates_detail, name='package_handover_document_media_updates_detail'),

    path('projects/<int:project_pk>/response-categories/', response_category_list, name='response_category_list'),
    path('projects/<int:project_pk>/response-categories/<int:pk>/', response_category_detail, name='response_category_detail'),

    path('media/private/<str:uuid>/', MediaViewSet.as_view({'get': 'retrieve_private'}), name='media_private_retrieve'),
    path('media/report/private/<str:uuid>/', MediaViewSet.as_view({'get': 'retrieve_private_report'}), name='report_private_retrieve'),
    path('media/project-snapshot/private/<str:uuid>/', MediaViewSet.as_view({'get': 'retrieve_private_project_snapshot'}), name='project_snapshot_private_retrieve'),

    path('users/csv/', UserViewSet.as_view({'get': 'generate_csv'}), name='user_generate_csv'),

    re_path(r'^', include(router.urls)),
    path('password-reset/', include('django_rest_passwordreset.urls', namespace='user')),

    path('health-check/', HealthCheckView.as_view({'get': 'check'}), name='health_check')
]
