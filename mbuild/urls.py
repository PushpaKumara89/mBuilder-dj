from django.conf import settings
from django.contrib.auth.models import Group
from django.urls import path, include, re_path
from django_cron.models import CronJobLog
from django_rest_passwordreset.models import ResetPasswordToken
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from django.contrib import admin
from rest_framework_api_key.models import APIKey
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken

from api.authentication import AnonymousBasicAuthentication


schema_view = get_schema_view(
    openapi.Info(
        title='MBuild API',
        default_version='v1',
        description='MBuild REST API Documentation',
        terms_of_service='https://www.google.com/policies/terms/',
        contact=openapi.Contact(email='admin@admin.com'),
        license=openapi.License(name='BSD License'),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    authentication_classes=(AnonymousBasicAuthentication,) if settings.ENV == 'production' else []
)

urlpatterns = [
    path('api/', include('api.urls')),
    path('admin/', admin.site.urls),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]

if settings.ENV == 'production':
    admin.site.unregister(APIKey)
    admin.site.unregister(Group)
    admin.site.unregister(CronJobLog)
    admin.site.unregister(ResetPasswordToken)
    admin.site.unregister(BlacklistedToken)
    admin.site.unregister(OutstandingToken)
