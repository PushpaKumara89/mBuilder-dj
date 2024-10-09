from djmoney.contrib.django_rest_framework import MoneyField
from rest_framework import fields, serializers

from api.http.serializers import ProjectNewsSerializer, UserSerializer, ResponseCategorySerializer
from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.serializers import MediaSerializer
from api.http.serializers.package_matrix.package_matrix_serializer import PackageMatrixSerializer
from api.models import Project, User


class ProjectSnapshotDataSerializer(BaseModelSerializer):
    class Meta:
        model = Project
        fields = (
            'id', 'name', 'number', 'image', 'image_id', 'status',
            'start_date', 'completion_date', 'created_at',
            'updated_at', 'show_estimated_man_hours', 'value', 'value_currency',
            'news', 'key_contacts', 'package_matrix', 'users', 'response_categories'
        )
        expandable_fields = {
            'company_admins': (serializers.SerializerMethodField, {'method_name': 'company_admins'})
        }

    id = fields.ReadOnlyField()
    name = fields.CharField(read_only=True)
    number = fields.CharField(read_only=True)
    image = MediaSerializer(read_only=True, expand=['expanded_project_snapshot_thumbnails.expanded_thumbnail_url'])
    status = fields.ChoiceField(choices=Project.Status.choices, read_only=True)
    image_id = serializers.PrimaryKeyRelatedField(read_only=True)
    start_date = fields.DateField(read_only=True)
    completion_date = fields.DateField(read_only=True)
    show_estimated_man_hours = fields.BooleanField(read_only=False)
    value = MoneyField(read_only=True, max_digits=12, decimal_places=2)

    news = ProjectNewsSerializer(many=True, source='projectnews_set')
    key_contacts = UserSerializer(many=True, expand=['expanded_deleted'])
    users = UserSerializer(many=True, expand=['expanded_user_company', 'expanded_deleted'])
    package_matrix = PackageMatrixSerializer(many=True, source='packagematrix_set', expand=[
        'expanded_package',
        'expanded_package_activity',
        'expanded_package_activity.expanded_package_activity_tasks',
        'expanded_companies',
        'expanded_project'
    ])
    response_categories = serializers.SerializerMethodField(method_name='get_response_categories')

    def company_admins(self, obj: Project):
        users = User.objects.select_related('company').filter(group=User.Group.COMPANY_ADMIN.value)
        return UserSerializer(users, expand=['expanded_user_company', 'expanded_deleted'], many=True).data

    def get_response_categories(self, obj: Project):
        response_categories = ResponseCategorySerializer(obj.responsecategory_set.order_by('name').all(), many=True)
        return sorted(response_categories.data, key=lambda response_category: response_category['name'])
