from django.core.files.storage import default_storage

from mbuild.settings import IMAGE_EXTENSIONS


class ReportUtilities:
    @classmethod
    def get_files_and_images(cls, media) -> dict:
        images = []
        files = []

        if not media:
            return {}

        for update_media in media:
            render_obj = {'name': update_media.name, 'link': cls.get_file_link(update_media)}
            if update_media.extension in IMAGE_EXTENSIONS:
                images.append(render_obj)
            else:
                files.append(render_obj)

        return {
            'images': images,
            'files': files
        }

    @classmethod
    def get_file_link(cls, media) -> str:
        return default_storage.url(media.name) if media.is_public else media.link

