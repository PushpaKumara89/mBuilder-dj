import csv

from io import StringIO
from typing import List, Any

from django.core.files.uploadedfile import SimpleUploadedFile

from api.models import Media
from api.services.media_entity_service import MediaEntityService


class CsvFileService:
    csv_file: SimpleUploadedFile = None

    def __init__(self, file_name: str, media_service: Any = MediaEntityService) -> None:
        if not file_name.endswith('.csv'):
            raise ValueError('File name does not end with: .csv')
        self.file_name = file_name
        self.media_service = media_service

    def create_file(self, col_titles: List[str], rows_data: List) -> SimpleUploadedFile:
        f = StringIO()

        writer = csv.writer(f)
        writer.writerow(col_titles)
        title_count = len(col_titles)

        for row in rows_data:
            if title_count != len(row):
                raise ValueError(f'File: {self.file_name}, the row is shorter than the col_titles. Row: {row}')
            writer.writerow(row)

        self.csv_file = SimpleUploadedFile(content=f.getvalue().encode('utf8'), name=self.file_name, content_type='text/csv')
        return self.csv_file

    def save_file_to_media(self) -> Media:
        return self.media_service().save_report({'file': self.csv_file, 'is_public': False})
