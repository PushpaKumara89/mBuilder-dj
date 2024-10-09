from rest_framework.reverse import reverse

from api.http.serializers import TaskSerializer
from api.models import Task
from api.tests.test import TestCase


class CommonTest(TestCase):
    fixtures = [
        'api/tests/fixtures/dumps/common.json',
    ]

    def test_filter_invalid_expandable_field(self):
        task = Task.objects.order_by('id').first()
        serializer = TaskSerializer(task, expand=['non_existing_field', 'expanded_updates'])

        self.assertNotIn('non_existing_field', serializer.data)

    def test_get_invalid_expandable_field(self):
        url = reverse('tasks_detail', kwargs={'project_pk': 5, 'pk': 2})
        self._log_in_as_superuser()
        response = self.client.get(url, {'expand': ['non_existing_field', 'expanded_updates']})

        self.assertOk(response)
        self.assertNotIn('non_existing_field', response.data)
