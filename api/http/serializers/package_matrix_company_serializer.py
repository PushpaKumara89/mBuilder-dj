from rest_framework import serializers
from rest_framework_bulk import BulkListSerializer, BulkSerializerMixin

from api.http.serializers.company_serializer import CompanySerializer
from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.serializers.package_matrix.package_matrix_serializer import PackageMatrixSerializer
from api.http.validators import UniqueTogetherValidator
from api.models import PackageMatrix, PackageMatrixCompany, Company
from rest_framework.fields import ReadOnlyField


class PackageMatrixCompanySerializer(BaseModelSerializer, BulkSerializerMixin):
    class Meta:
        model = PackageMatrixCompany
        fields = ('id', 'package_matrix', 'company',)
        list_serializer_class = BulkListSerializer
        validators = [
            UniqueTogetherValidator(
                queryset=PackageMatrixCompany.objects.all(),
                fields=('package_matrix', 'company',)
            )
        ]
        expandable_fields = {
            'expanded_package_matrix': (PackageMatrixSerializer, {'source': 'package_matrix'}),
            'expanded_company': (CompanySerializer, {'source': 'company'}),
        }

    id = ReadOnlyField()
    package_matrix = serializers.PrimaryKeyRelatedField(required=True, queryset=PackageMatrix.objects.all())
    company = serializers.PrimaryKeyRelatedField(required=True, queryset=Company.objects.all())
