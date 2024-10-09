from rest_framework.exceptions import PermissionDenied
from rest_framework_mongoengine.viewsets import ModelViewSet


class MongoEngineModelViewSet(ModelViewSet):
    _request_permissions = []

    def get_permissions(self):
        try:
            self.permission_classes = self._request_permissions[self.action]

            return super().get_permissions()
        except:
            raise PermissionDenied()

    def get_serializer(self, *args, **kwargs):
        request_context = {'request': self.request}

        if 'project_pk' in self.kwargs:
            request_context['project_pk'] = self.kwargs['project_pk']

        kwargs['context'] = {**kwargs['context'], **request_context} if 'context' in kwargs else request_context

        return self.get_serializer_class()(*args, **kwargs)
