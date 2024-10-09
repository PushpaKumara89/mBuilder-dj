import json
import shutil
from io import BytesIO
from pathlib import Path

import pendulum
from PIL import Image
from django.conf import settings
from django.core import mail
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django_redis import get_redis_connection
from freezegun import freeze_time
from mongoengine.connection import get_connection
from rest_framework import status
from rest_framework.test import APITestCase, APITransactionTestCase
from rest_framework_simplejwt.tokens import RefreshToken
from api.models import User, Event
from api.utilities.tests_utilities import load_fixture, load_json


def data_provider(data_provider_function):
    def wrapped_test(test_function):
        def call_wrapped_test_with_provided_data(self):
            for data in data_provider_function(self):
                data = data if type(data) in [list, tuple] else [data]
                test_function(self, *data)

        return call_wrapped_test_with_provided_data

    return wrapped_test


def get_mongodb_test_database_name():
    return get_connection().get_default_database().name


class BaseTestCase:
    mongodb_name = get_mongodb_test_database_name()
    responses_fixtures_dir = 'api/tests/fixtures/responses'
    dumps_fixtures_dir = 'api/tests/fixtures/dumps'
    requests_fixtures_dir = 'api/tests/fixtures/requests'
    mongo_fixtures = list()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.frozen_time = freeze_time('2020-02-02')
        self.frozen_time.start()

    def setUp(self) -> None:
        connection = get_connection()
        connection.drop_database(self.mongodb_name)

        if len(self.mongo_fixtures) > 0:
            call_command('load_mongodb_fixtures', *self.mongo_fixtures)

        super().setUp()

    def force_login_user(self, value, field='pk'):
        user = User.objects.get(**{field: value})
        self.client.force_login(user)

    def save_fixture(self, data, path):
        with open(path, 'w') as f:
            json.dump(data, f, indent=True)

    def save_bytes_fixture(self, path, data):
        with open(path, 'wb') as f:
            f.write(data)

    def save_fixture_email(self, data, path):
        with open(path, 'w') as f:
            f.write(data)

    def load_video_fixture(self, path: str) -> SimpleUploadedFile:
        return self.load_binary_fixture(path, 'video/mp4')

    def load_pdf_fixture(self, path: str) -> SimpleUploadedFile:
        return self.load_binary_fixture(path, 'text/pdf')

    def load_svg_fixture(self, path: str) -> SimpleUploadedFile:
        return self.load_binary_fixture(path, 'image/svg+xml')

    def load_heic_fixture(self, path: str) -> SimpleUploadedFile:
        return self.load_binary_fixture(path, 'image/heic')

    def load_binary_fixture(self, path: str, content_type: str) -> SimpleUploadedFile:
        with open(path, 'rb') as f:
            filename = path.split('/')[-1]
            return SimpleUploadedFile(content=f.read(), content_type=content_type, name=filename)

    def assertEventsExist(self, response_fixture, export=False):
        if export or settings.EXPORT_EVENTS:
            events = json.loads(Event.objects().to_json())
            for event in events:
                self._format_mongo_fields(event)

            self.save_fixture(events, self.responses_fixtures_dir + response_fixture)

        events_assertion = load_json(self.responses_fixtures_dir + response_fixture)
        for event in events_assertion:
            self._format_mongo_fields(event)
            self.assertTrue(len(Event.objects(**event)) > 0)

    # Avoid unnecessary fixture edit after dumping data from DB
    def _format_mongo_fields(self, event: dict):
        if '_id' in event:
            del event['_id']

        if 'created_at' in event:
            del event['created_at']

        if 'updated_at' in event:
            del event['updated_at']

        for field_name, value in event.items():
            if type(value) is dict and '$date' in value:
                # Date saving in timestamp with milliseconds.
                # Remove them to successfully convert the date.
                if type(value['$date']) is int:
                    event[field_name] = pendulum.from_timestamp(value['$date'] // 1000).to_datetime_string()
                else:
                    event[field_name] = value['$date']

    def assertEmailEquals(self, emails, export=False):
        sent_emails = mail.outbox

        self.assertGreaterEqual(len(sent_emails), len(emails))

        for index, sent_email in enumerate(sent_emails):
            try:
                fixture = emails[index]['fixture']

                if export:
                    self.save_fixture_email(sent_email.body, fixture)

                expected_subject = emails[index].get('subject')
                expected_from_email = emails[index]['from_email']
                to_email = emails[index]['to']
                expected_to_email_sample = sent_email.to
                expected_rendered_email = load_fixture(fixture)

                sorted(to_email)
                sorted(expected_to_email_sample)

                self.assertEquals(expected_subject, sent_email.subject)
                self.assertEquals(expected_from_email, sent_email.from_email)
                self.assertListEqual(expected_to_email_sample, to_email)
                self.assertEquals(expected_rendered_email, sent_email.body)
            except IndexError:
                print('More email sent for %s | %s', (sent_email.to, sent_email.from_email))
                continue

    def assertSoftDeleted(self, model_class, kwfilters, filters=None):
        if filters is None:
            filters = []

        if type(kwfilters) is int:
            kwfilters = {'pk': kwfilters}

        self.assertTrue(model_class.deleted_objects.filter(*filters, **kwfilters).exists())

    def assertHardDeleted(self, model_class, filters):
        if type(filters) is int:
            filters = {'pk': filters}

        self.assertTrue(not model_class.all_objects.filter(**filters).exists())

    def assertDatabaseHas(self, model_class, kwfilters, filters=None):
        if filters is None:
            filters = []

        if type(kwfilters) is int:
            kwfilters = {'pk': kwfilters}

        self.assertTrue(model_class.objects.filter(*filters, **kwfilters).exists())

    def assertDatabaseMissing(self, model_class, filters):
        if type(filters) is int:
            filters = {'pk': filters}

        self.assertTrue(not model_class.objects.filter(**filters).exists())

    def assertEqualsFixture(self, data, path_to_response_fixture, export: bool = False):
        path_to_fixture = self.responses_fixtures_dir + path_to_response_fixture
        if export:
            self.save_fixture(data, path_to_fixture)

        fixture = load_json(path_to_fixture)
        self.assertEquals(data, fixture)

    def assertNoContent(self, response):
        self.assertEquals(response.status_code, status.HTTP_204_NO_CONTENT)

    def assertOk(self, response):
        self.assertEquals(response.status_code, status.HTTP_200_OK)

    def assertCreated(self, response):
        self.assertEquals(response.status_code, status.HTTP_201_CREATED)

    def assertForbidden(self, response):
        self.assertEquals(response.status_code, status.HTTP_403_FORBIDDEN)

    def assertNotFound(self, response):
        self.assertEquals(response.status_code, status.HTTP_404_NOT_FOUND)

    def assertBadRequest(self, response):
        self.assertEquals(response.status_code, status.HTTP_400_BAD_REQUEST)

    def assertUnauthorized(self, response):
        self.assertEquals(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def assertConflict(self, response):
        self.assertEquals(response.status_code, status.HTTP_409_CONFLICT)

    def generate_fake_image(self, name='fakeimage.png'):
        file = BytesIO()
        image = Image.new('RGBA', size=(100, 100), color=(155, 0, 0))
        image.save(file, 'png')
        file.name = name
        file.seek(0)

        return file

    def generate_and_save_fake_image(self, name='fakeimage.png'):
        fss = FileSystemStorage()

        file = self.generate_fake_image(name)
        fss.save(name=name, content=file)

        return file

    def load_and_save_fake_pdf(self, name='fake_file.pdf', path='fake_file.pdf'):
        fss = FileSystemStorage()

        file = self.load_pdf_fixture(path)
        fss.save(name=name, content=file)

        return file

    def load_request_fixture(self, path: str):
        return load_json(self.requests_fixtures_dir + path)

    def load_response_fixture(self, path: str):
        return load_json(self.responses_fixtures_dir + path)

    def tearDown(self) -> None:
        super().tearDown()
        get_redis_connection('default').flushall()

        # Remove temporary folder with media files.
        if Path('media').exists():
            shutil.rmtree('media')

    @staticmethod
    def get_user_token(user) -> RefreshToken:
        return RefreshToken.for_user(user)

    def _log_in_as_superuser(self, *args, **kwargs):
        superuser = self._get_superuser(*args, **kwargs)
        self.force_login_user(superuser.pk)

    def _log_in_as_staff(self, *args, **kwargs):
        staff = self._get_staff(*args, **kwargs)
        self.force_login_user(staff.pk)

    def _log_in_as_client(self, *args, **kwargs):
        client = self._get_client(*args, **kwargs)
        self.force_login_user(client.pk)

    def _log_in_as_subcontractor(self, *args, **kwargs):
        subcontractor = self._get_subcontractor(*args, **kwargs)
        self.force_login_user(subcontractor.pk)

    def _log_in_as_consultant(self, *args, **kwargs):
        consultant = self._get_consultant(*args, **kwargs)
        self.force_login_user(consultant.pk)

    def _log_in_as_company_admin(self, *args, **kwargs):
        company_admin = self._get_company_admin(*args, **kwargs)
        self.force_login_user(company_admin.pk)

    def _log_in_as_admin(self, *args, **kwargs):
        admin = self._get_admin(*args, **kwargs)
        self.force_login_user(admin.pk)

    def _log_in_as_user(self, *args, **kwargs):
        user = self._get_user(*args, **kwargs)
        self.force_login_user(user.pk)

    def _log_in_as_manager(self, *args, **kwargs):
        manager = self._get_manager(*args, **kwargs)
        self.force_login_user(manager.pk)

    def _get_staff(self, *args, **kwargs):
        return self._get_user(*args, **kwargs, is_staff=True, is_superuser=False)

    def _get_client(self, *args, **kwargs):
        return self._get_user(*args, **kwargs, groups=User.Group.CLIENT.value, is_superuser=False)

    def _get_subcontractor(self, *args, **kwargs):
        return self._get_user(*args, **kwargs, groups=User.Group.SUBCONTRACTOR.value, is_superuser=False)

    def _get_consultant(self, *args, **kwargs):
        return self._get_user(*args, **kwargs, groups=User.Group.CONSULTANT.value, is_superuser=False)

    def _get_superuser(self, *args, **kwargs):
        return self._get_user(*args, **kwargs, is_superuser=True)

    def _get_company_admin(self, *args, **kwargs):
        return self._get_user(*args, **kwargs, groups=User.Group.COMPANY_ADMIN.value)

    def _get_admin(self, *args, **kwargs):
        return self._get_user(*args, **kwargs, groups=User.Group.ADMIN.value)

    def _get_manager(self, *args, **kwargs):
        return self._get_user(*args, **kwargs, groups=User.Group.MANAGER.value)

    def _get_user(self, *args, **kwargs):
        return User.objects.filter(*args, **kwargs).order_by('id').first()

    def _exclude_expanded_fields_from_response(self, response):
        for key, response_item in enumerate(response.data):
            response.data[key] = {key: value for key, value in response_item.items() if not key.startswith('expanded')}

    def _remove_media_fields_with_hash(self, response):
        for response_item in response.data:
            if 'expanded_media' in response_item:
                del response_item['expanded_media']['hash']
                del response_item['expanded_media']['link']


class TestCase(BaseTestCase, APITestCase):
    pass


class TransactionTestCase(BaseTestCase, APITransactionTestCase):
    serialized_rollback = True
