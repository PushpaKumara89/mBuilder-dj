from io import BytesIO
from math import ceil
from typing import Optional, Tuple

import ffmpeg
from django.core.files.uploadedfile import InMemoryUploadedFile
from sentry_sdk import utils, push_scope, capture_exception
from storages.base import BaseStorage

from api.models import Media, MediaThumbnail
from api.utilities.pdf_utilities import convert_pdf_page_to_image
from mbuild.settings import VIDEO_EXTENSIONS


class ThumbnailService:
    VIDEO_MIN_DURATION: int = 3
    VIDEO_THUMBNAIL_CUT_OFF_SECOND: int = 3

    def get_video_stream_info(self, file_path: str) -> Optional[dict]:
        file_extension = file_path.split('?')[0].split('.')[-1].lower()
        if file_extension not in VIDEO_EXTENSIONS:
            return None

        try:
            probe = ffmpeg.probe(file_path)
        except ffmpeg.Error as e:
            self._capture_error(e)

            return None

        return next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)

    def get_pdf_first_page(self, media: Media, storage: BaseStorage,
                           dpi: Optional[Tuple] = (MediaThumbnail.PDF_THUMBNAIL_DPI_SIZES.width,
                                                   MediaThumbnail.PDF_THUMBNAIL_DPI_SIZES.height)
                           ) -> Optional[InMemoryUploadedFile]:
        bytes_input = convert_pdf_page_to_image(page_number=1, pdf_data=BytesIO(storage.open(media.name).file.read()),
                                                image_options={'dpi': dpi})
        if bytes_input is None:
            return None

        return self._get_in_memory_file(media=media, bytes_input=bytes_input)

    def get_video_thumbnail(self, media: Media, video_stream: dict, file_path: str) -> Optional[InMemoryUploadedFile]:
        if all(field in video_stream.keys() for field in ('avg_frame_rate', 'duration', 'nb_frames')):
            frame_rate = self._get_frame_rate(video_stream)
            frame_num = frame_rate * self.VIDEO_THUMBNAIL_CUT_OFF_SECOND \
                if int(float(video_stream['duration'])) >= self.VIDEO_MIN_DURATION \
                else int(ceil(int(video_stream['nb_frames']) / 2))
        else:
            return None

        output, _ = self._cut_frame(file_path, frame_num)

        if isinstance(output, OSError):
            output, _ = self._cut_frame(file_path, frame_num - 1)

        if isinstance(output, Exception):
            return None

        return self._get_in_memory_file(media=media, bytes_input=BytesIO(output),
                                        extension='jpeg', content_type='image/jpeg')

    def _cut_frame(self, file_path: str, frame_num: int, /) -> tuple:
        try:
            return (
                ffmpeg
                .input(file_path)
                .filter('select', 'gte(n,{})'.format(frame_num - 1))
                .output('pipe:', vframes=1, format='image2pipe', vcodec='mjpeg')
                .run(capture_stdout=True, capture_stderr=True)
            )
        except Exception as e:
            self._capture_error(e)

            return e, None

    def _get_frame_rate(self, video_stream: dict, /) -> int:
        frame_rate = video_stream['avg_frame_rate'].split('/')
        return int(int(frame_rate[0]) / int(frame_rate[1]))

    def _get_in_memory_file(self, media: Media, bytes_input: BytesIO, extension='png',
                            content_type='image/png') -> InMemoryUploadedFile:
        name = '.'.join(media.name.split('.')[0:-1])
        return InMemoryUploadedFile(file=bytes_input, field_name=None, name=f'{name}.{extension}',
                                    content_type=content_type, size=bytes_input.getbuffer().nbytes, charset=None)

    def _capture_error(self, error: ffmpeg.Error | Exception) -> None:
        # Increase error message max length limit to catch all the text.
        default_string_length = utils.MAX_STRING_LENGTH
        utils.MAX_STRING_LENGTH = 4096

        with push_scope() as scope:
            if isinstance(error, ffmpeg.Error):
                text = error.stderr.decode('utf8')
            else:
                text = str(error)

            scope.set_extra('Error message', {'text': text})
            capture_exception(error)

        utils.MAX_STRING_LENGTH = default_string_length
