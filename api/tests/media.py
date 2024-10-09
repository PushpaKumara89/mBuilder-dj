from copy import deepcopy
from unittest.mock import patch

import PIL
from PIL import Image
from PIL.Image import DecompressionBombError
from django.core.files.storage import FileSystemStorage

from api.models import Media
from api.models.media_thumbnail import MediaThumbnail
from api.services.media_thumbnail_entity_service import MediaThumbnailEntityService
from api.storages import AzurePrivateMediaStorage
from api.tests.test import TestCase, data_provider
from api.utilities.tests_utilities import load_json


class MediaTest(TestCase):
    fixtures = ['api/tests/fixtures/dumps/media.json']
    fss = FileSystemStorage()

    def mock_media_link(self, *args, **kwargs):
        return 'http://localhost/image.jpg'

    def mock_save(self, *args, **kwargs):
        return self.fss.save(*args, **kwargs)

    @patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    @patch('api.storages.AzurePrivateMediaStorage.save', fss.save)
    def test_authorized_create(self):
        new_media = {'file': self.generate_fake_image()}
        assertion_data = load_json(self.responses_fixtures_dir + '/media/created_entity_assertion_data.json')
        user = self._get_user()

        self.force_login_user(user.pk)
        response = self.client.post('/api/media/', new_media, format='multipart')

        self.assertCreated(response)
        self.assertDatabaseHas(Media, assertion_data)
        self.assertDatabaseHas(MediaThumbnail, {'original_media__name': 'fakeimage.png', 'thumbnail__isnull': False})

    @patch('api.storages.AzurePrivateMediaStorage.save', fss.save)
    @patch('api.storages.AzurePrivateMediaStorage.url', fss.path)
    @patch('django.core.files.storage.FileSystemStorage.url', fss.path)
    @patch('api.storages.AzurePrivateMediaStorage.open', fss.open)
    @patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    @patch('api.services.media_entity_service.MediaEntityService._generate_file_name', lambda *args, **kwargs: 'fakeimage.png')
    def test_authorized_bulk_create(self):
        new_media = {'uuid_1': self.generate_fake_image(), 'uuid_2': self.generate_fake_image()}
        user = self._get_user()

        self.force_login_user(user.pk)
        response = self.client.post('/api/media/bulk-create/', new_media, format='multipart')

        self.assertCreated(response)
        self.assertDatabaseHas(Media, {'local_id': 'uuid_1', 'name': 'fakeimage.png'})
        self.assertDatabaseHas(Media, {'local_id': 'uuid_2', 'name__contains': 'fakeimage'})
        self.assertDatabaseHas(MediaThumbnail, {'original_media__local_id': 'uuid_1', 'thumbnail__isnull': False})
        self.assertDatabaseHas(MediaThumbnail, {'original_media__local_id': 'uuid_2', 'thumbnail__isnull': False})
        # todo Rework creating multiple media with unique hash
        # self.assertEventsExist('/media/bulk_create_events_assertion.json')

    @patch('api.storages.AzurePrivateMediaStorage.save', fss.save)
    @patch('api.storages.AzurePrivateMediaStorage.open', fss.open)
    def test_unauthorized_create(self):
        new_media = {'file': self.generate_fake_image()}
        response = self.client.post('/api/media/', new_media, format='multipart')

        self.assertCreated(response)

    def test_get_authorized(self):
        user = self._get_user()
        self.force_login_user(user.pk)
        response = self.client.get('/api/media/1/')

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/media/get_media.json')

    @patch('api.storages.AzurePrivateMediaStorage.url')
    def test_get_private_by_authorized(self, mock_url):
        mock_url.return_value = 'https://teststorage.com/image.png'
        user = self._get_user()

        self.force_login_user(user.pk)
        response = self.client.get('/api/media/private/c0b7387122b04fee87602fce2a48028b/')

        self.assertRedirects(response, 'https://teststorage.com/image.png', fetch_redirect_response=False)

    @patch('api.storages.AzurePrivateMediaStorage.url')
    def test_get_private_by_unauthorized(self, mock_url):
        mock_url.return_value = 'https://teststorage.com/image.png'
        response = self.client.get('/api/media/private/c0b7387122b04fee87602fce2a48028b/')

        self.assertRedirects(response, 'https://teststorage.com/image.png', fetch_redirect_response=False)

    def test_delete_by_superuser(self):
        superuser = self._get_user(is_superuser=True)
        self.force_login_user(superuser.pk)
        response = self.client.delete('/api/media/1/')

        self.assertNoContent(response)
        self.assertSoftDeleted(Media, 1)
        self.assertEventsExist('/media/delete_events_assertion.json')

    def test_forbid_delete_by_non_superuser(self):
        non_superuser = self._get_user(is_superuser=False)
        self.force_login_user(non_superuser.pk)
        response = self.client.delete('/api/media/1/')

        self.assertForbidden(response)

    def test_unauthorized_delete(self):
        response = self.client.delete('/api/media/1/')

        self.assertUnauthorized(response)

    def test_update_by_staff(self):
        update_media = self.load_request_fixture('/media/update_media.json')
        staff = self._get_user(is_staff=True)

        self.force_login_user(staff.pk)
        response = self.client.put('/api/media/1/', update_media)

        self.assertOk(response)
        self.assertDatabaseHas(Media, update_media)
        self.assertEventsExist('/media/update_events_assertion.json')

    def test_forbid_update_by_non_staff(self):
        update_media = self.load_request_fixture('/media/update_media.json')
        non_staff = self._get_user(is_staff=False)

        self.force_login_user(non_staff.pk)
        response = self.client.put('/api/media/1/', update_media)

        self.assertForbidden(response)

    def test_unauthorized_update(self):
        update_media = self.load_request_fixture('/media/update_media.json')
        response = self.client.put('/api/media/1/', update_media)

        self.assertUnauthorized(response)

    def get_filters(self):
        return (
            (
                {'all': True},
                '/media/get_all.json'
            ),
            (
                {'sort': '-name'},
                '/media/get_all_desc_order.json'
            ),
            (
                {'page': 2, 'per_page': 2},
                '/media/get_all_page_per_page.json'
            )
        )

    @data_provider(get_filters)
    def test_search_by_staff(self, filters, fixture):
        staff = self._get_user(is_staff=True)
        self.force_login_user(staff.pk)
        response = self.client.get('/api/media/', filters)

        self.assertOk(response)
        self.assertEqualsFixture(response.data, fixture)

    def test_search_by_non_staff(self):
        non_staff = self._get_user(is_staff=False)
        self.force_login_user(non_staff.pk)
        response = self.client.get('/api/media/', {'all': 1})

        self.assertForbidden(response)

    def test_unauthorized_search(self):
        response = self.client.get('/api/media/', {'all': 1})

        self.assertUnauthorized(response)

    @patch('api.storages.AzurePrivateMediaStorage.save', fss.save)
    @patch('api.storages.AzurePrivateMediaStorage.url', fss.path)
    @patch('django.core.files.storage.FileSystemStorage.url', fss.path)
    @patch('api.storages.AzurePrivateMediaStorage.open', fss.open)
    @patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    def test_create_thumbnails_for_long_video(self):
        filename = 'more_then_three_seconds_video.mp4'
        fixture_path = f'{self.requests_fixtures_dir}/media/{filename}'
        new_media = {'file': self.load_video_fixture(fixture_path)}
        assertion_data = load_json(self.responses_fixtures_dir + '/media/create_long_video_thumbnails_database_assertion.json')

        self._log_in_as_superuser()
        response = self.client.post('/api/media/', new_media, format='multipart')

        self.assertCreated(response)
        self.assertDatabaseHas(Media, assertion_data)
        self.assertDatabaseHas(
            MediaThumbnail,
            {
                'original_media__name': filename,
                'width__isnull': True,
                'height__isnull': True
            },
        )

    @patch('api.storages.AzurePrivateMediaStorage.save', fss.save)
    @patch('api.storages.AzurePrivateMediaStorage.url', fss.path)
    @patch('django.core.files.storage.FileSystemStorage.url', fss.path)
    @patch('api.storages.AzurePrivateMediaStorage.open', fss.open)
    @patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    def test_create_thumbnails_for_not_allowed_video_extension(self):
        filename = 'file.dwg'
        new_media = {'file': self.generate_fake_image(filename)}

        self._log_in_as_superuser()
        response = self.client.post('/api/media/', new_media, format='multipart')

        self.assertCreated(response)
        self.assertDatabaseHas(Media, {'name': filename})
        self.assertDatabaseMissing(
            MediaThumbnail, {'original_media__name': filename},
        )

    @patch('api.storages.AzurePrivateMediaStorage.save', fss.save)
    @patch('api.storages.AzurePrivateMediaStorage.open', fss.open)
    @patch('api.storages.AzurePrivateMediaStorage.url', fss.path)
    @patch('django.core.files.storage.FileSystemStorage.url', fss.path)
    @patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    def test_create_thumbnails_for_short_video(self):
        filename = 'less_then_three_seconds_video.mp4'
        fixture_path = f'{self.requests_fixtures_dir}/media/{filename}'
        new_media = {'file': self.load_video_fixture(fixture_path)}
        assertion_data = load_json(self.responses_fixtures_dir + '/media/create_short_video_thumbnails_database_assertion.json')

        self._log_in_as_superuser()
        response = self.client.post('/api/media/', new_media, format='multipart')

        self.assertCreated(response)
        self.assertDatabaseHas(Media, assertion_data)
        self.assertDatabaseHas(
            MediaThumbnail,
            {
                'original_media__name': filename,
                'width__isnull': True,
                'height__isnull': True,
            },
        )

    @patch('api.storages.AzurePrivateMediaStorage.save', fss.save)
    @patch('api.storages.AzurePrivateMediaStorage.open', fss.open)
    @patch('api.storages.AzurePrivateMediaStorage.url', fss.path)
    @patch('django.core.files.storage.FileSystemStorage.url', fss.path)
    @patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    def test_create_thumbnails_for_pdf(self):
        filename = 'test.pdf'
        fixture_path = f'{self.requests_fixtures_dir}/media/{filename}'
        new_media = {'file': self.load_pdf_fixture(fixture_path)}
        assertion_data = load_json(self.responses_fixtures_dir + '/media/create_pdf_thumbnail_database_assertion.json')

        self._log_in_as_superuser()
        response = self.client.post('/api/media/', new_media, format='multipart')

        self.assertCreated(response)
        self.assertDatabaseHas(Media, assertion_data)
        self.assertDatabaseHas(
            MediaThumbnail,
            {
                'original_media__name': filename,
                'width__isnull': True,
                'height__isnull': True,
            },
        )

    @patch('api.storages.AzurePrivateMediaStorage.save', fss.save)
    @patch('api.storages.AzurePrivateMediaStorage.open', fss.open)
    @patch('api.storages.AzurePrivateMediaStorage.url', fss.path)
    @patch('django.core.files.storage.FileSystemStorage.url', fss.path)
    @patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    def test_create_thumbnails_for_svg(self):
        filename = 'image.svg'
        fixture_path = f'{self.requests_fixtures_dir}/media/{filename}'
        new_media = {'file': self.load_svg_fixture(fixture_path)}
        assertion_data = load_json(self.responses_fixtures_dir + '/media/create_svg_thumbnail_database_assertion.json')

        self._log_in_as_superuser()
        response = self.client.post('/api/media/', new_media, format='multipart')

        self.assertCreated(response)
        self.assertDatabaseHas(Media, assertion_data)
        self.assertDatabaseHas(
            MediaThumbnail,
            {
                'original_media__name': filename,
                'width__isnull': True,
                'height__isnull': True,
            },
        )

    @patch('api.storages.AzurePrivateMediaStorage.save', fss.save)
    @patch('api.storages.AzurePrivateMediaStorage.open', fss.open)
    @patch('api.storages.AzurePrivateMediaStorage.url', fss.path)
    @patch('django.core.files.storage.FileSystemStorage.url', fss.path)
    @patch('api.services.media_entity_service.MediaEntityService._generate_link', mock_media_link)
    def test_create_thumbnails_for_heic(self):
        filename = 'image.heic'
        fixture_path = f'{self.requests_fixtures_dir}/media/{filename}'
        new_media = {'file': self.load_heic_fixture(fixture_path)}
        assertion_data = load_json(self.responses_fixtures_dir + '/media/create_heic_thumbnail_database_assertion.json')

        self._log_in_as_superuser()
        response = self.client.post('/api/media/', new_media, format='multipart')

        self.assertCreated(response)
        self.assertDatabaseHas(Media, assertion_data)
        self.assertDatabaseHas(
            MediaThumbnail,
            {
                'original_media__name': filename,
                'width__isnull': True,
                'height__isnull': True,
            },
        )

    def test_get_with_thumbnails(self):
        self._log_in_as_superuser()
        response = self.client.get('/api/media/7/', {'expand': ['expanded_thumbnails.expanded_thumbnail', 'expanded_project_snapshot_thumbnails.expanded_thumbnail']})

        self.assertOk(response)
        self.assertEqualsFixture(response.data, '/media/get_media_with_thumbnails.json')

    @patch('PIL.Image.open')
    def test_open_image_with_huge_resolution(self, pil_image_mock):
        """
        Check error DecompressionBombError caught and image opened

        :param pil_image_mock:
        :return:
        """
        media = Media.objects.get(id=1)
        thumbnail = deepcopy(media)

        self.generate_and_save_fake_image('troom.png')
        image = Image.open(self.fss.open(media.name))

        pil_image_mock.side_effect = [DecompressionBombError, image]

        for thumbnail in MediaThumbnailEntityService().get_thumbnails_if_not_exists(
            media=media, thumbnail=thumbnail, storage=self.fss,
            sizes=MediaThumbnail.PROJECT_SNAPSHOT_THUMBNAIL_SIZES
        ):
            self.assertIsNotNone(thumbnail)
            self.assertIsNone(PIL.Image.MAX_IMAGE_PIXELS)
