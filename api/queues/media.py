from api.queues.core.base import use_rq_if_configured

from api.queues.celery.media import generate_project_image_thumbnails as generate_project_image_thumbnails_celery, \
    create_thumbnails as create_thumbnails_celery
from api.queues.rq.media import generate_project_image_thumbnails as generate_project_image_thumbnails_rq, \
    create_thumbnails as create_thumbnails_rq

from api.models import Media


@use_rq_if_configured(generate_project_image_thumbnails_rq)
def generate_project_image_thumbnails(image_file_name: str) -> None:
    generate_project_image_thumbnails_celery.delay(image_file_name)


@use_rq_if_configured(create_thumbnails_rq)
def create_thumbnails(media: Media) -> None:
    create_thumbnails_celery.delay(media)
