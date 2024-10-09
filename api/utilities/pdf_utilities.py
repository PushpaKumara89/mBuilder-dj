import os
import tempfile
from io import BytesIO
from typing import Optional, Tuple

import pydash
import fitz
from PIL import Image


DEFAULT_PDF_DPI = 72
MAX_PDF_IMAGE_RESOLUTION = 6000


def convert_pdf_page_to_image(page_number: int, pdf_data: BytesIO, image_options=None) -> \
        Optional[BytesIO]:
    if image_options is None:
        image_options = {
            'dpi': (DEFAULT_PDF_DPI, DEFAULT_PDF_DPI),
            'alpha_layer': None
        }

    document = fitz.open(stream=pdf_data, filetype='pdf')

    b = BytesIO()
    try:
        page = document[page_number - 1]
        scale_x, scale_y, desired_dpi = calculate_scaling_factors((DEFAULT_PDF_DPI, DEFAULT_PDF_DPI),
                                                                  pydash.get(image_options, 'dpi'),
                                                                  MAX_PDF_IMAGE_RESOLUTION,
                                                                  page.rect.width, page.rect.height)

        matrix = fitz.Matrix(scale_x, scale_y)
        pixmap = page.get_pixmap(matrix=matrix)

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            pixmap.save(temp_file.name, 'png')

        with Image.open(temp_file.name) as image:
            alpha_layer = pydash.get(image_options, 'alpha_layer')

            if alpha_layer is not None:
                image.putalpha(alpha_layer)

            image.save(b, 'png', dpi=desired_dpi)

        os.remove(temp_file.name)

        return b
    except IndexError:
        return None
    finally:
        document.close()


def calculate_scaling_factors(current_dpi: Tuple[int, int], desired_dpi: Tuple[int, int], max_resolution: int,
                              width: int, height: int) ->  Tuple[float, float, Tuple[int, int]]:
    scale_x = desired_dpi[0] / current_dpi[0]
    scale_y = desired_dpi[1] / current_dpi[1]

    new_width = int(width * scale_x)
    new_height = int(height * scale_y)

    if new_width > max_resolution or new_height > max_resolution:
        scaling_factor = min(max_resolution / new_width, max_resolution / new_height)
        scale_x *= scaling_factor
        scale_y *= scaling_factor

        desired_dpi = (
            int(desired_dpi[0] * scaling_factor),
            int(desired_dpi[1] * scaling_factor),
        )

    return scale_x, scale_y, desired_dpi
