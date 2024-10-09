from mbuild.settings import app as celery_app

from api.queues.core.media import generate_project_image_thumbnails as generate_project_image_thumbnails_core, \
    create_thumbnails as create_thumbnails_core

from api.models import Media


@celery_app.task(queue='thumbnails', time_limit=3600)
def generate_project_image_thumbnails(image_file_name: str) -> None:
    generate_project_image_thumbnails_core(image_file_name)


@celery_app.task(queue='thumbnails', time_limit=3600)
def create_thumbnails(media: Media) -> None:
    create_thumbnails_core(media)
