import io
import os
import tempfile

import pyqrcode
import textwrap
from PIL import Image
from pydash import find_index
from reportlab.pdfgen import canvas
from rest_framework import serializers

from api.http.serializers.base_model_serializer import BaseModelSerializer
from api.http.serializers.location_matrix.location_matrix_serializer import LocationMatrixSerializer
from api.models import LocationMatrix, Project


class LocationMatrixQRCodesSerializer(BaseModelSerializer):
    class Meta:
        model = LocationMatrix
        fields = ('project', 'building', 'level', 'area',)

    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all(), required=True)
    building = serializers.ListField(child=serializers.CharField(max_length=255, required=True), required=False)
    level = serializers.ListField(child=serializers.CharField(max_length=255, required=True), required=False)
    area = serializers.ListField(child=serializers.CharField(max_length=255, required=True), required=False)

    def generate(self):
        project = self.validated_data['project']
        buildings = self.__get_formatted_list_of_buildings_levels_areas()

        x_margin = 15
        y_margin = 30
        box_width = 110
        box_height = 60
        qr_code_x_margin = x_margin + 5
        qr_code_y_margin = y_margin + 5
        qr_code_size = 50

        margin_between_boxes = 5
        text_font_size = 6
        project_text_margin = 28
        building_level_text_margin = 44
        area_text_margin = 53

        max_row_items = 5
        max_rows_per_page = 13

        buffer = io.BytesIO()

        page = canvas.Canvas(buffer)
        yield page.getpdfdata()

        row_index = 0

        def draw_row(building_name, level_name, area_name=None):
            qrcode_path = self.__generate_qr_code_png(project.pk, building_name, level_name, area_name)
            self.__paste_logo_inside_qr_code_png(qrcode_path, qr_code_size)

            item_y_margin = y_margin + box_height * row_index if row_index > 0 else y_margin
            item_qr_code_y_margin = qr_code_y_margin + box_height * row_index if row_index > 0 else qr_code_y_margin

            for i in range(max_row_items):
                item_x_margin = x_margin + ((box_width + margin_between_boxes) * i) if i > 0 else x_margin
                item_qr_code_x_margin = qr_code_x_margin + ((box_width + margin_between_boxes) * i) if i > 0 else qr_code_x_margin
                item_text_x_margin = qr_code_size + ((box_width + margin_between_boxes) * i)
                item_project_text_x = item_text_x_margin + project_text_margin if i > 0 else qr_code_size + project_text_margin
                item_building_level_text_x = item_text_x_margin + building_level_text_margin if i > 0 else qr_code_size + building_level_text_margin
                item_area_text_x = item_text_x_margin + area_text_margin if i > 0 else qr_code_size + area_text_margin

                page.drawImage('api/static/qr-codes/images/border.png', x=item_x_margin, y=item_y_margin, mask='auto', width=box_width, height=box_height)
                page.drawImage(qrcode_path, x=item_qr_code_x_margin, y=item_qr_code_y_margin, mask='auto', width=qr_code_size, height=qr_code_size)

                self.__drawRotatedText(page, project.name, 'Helvetica-Bold', text_font_size, item_project_text_x, item_y_margin, box_height, max_lines=2)
                self.__drawRotatedText(page, '%s / %s' % (building['name'], level['name']), 'Helvetica', text_font_size, item_building_level_text_x, item_y_margin,box_height)
                if area_name is not None:
                    self.__drawRotatedText(page, area_name, 'Helvetica', text_font_size, item_area_text_x, item_y_margin, box_height, max_lines=3)

            os.remove(qrcode_path)

        for building in buildings:
            for level_index, level in enumerate(building['levels']):
                draw_row(building['name'], level['name'])

                row_index = row_index + 1
                if row_index == max_rows_per_page:
                    row_index = 0
                    page.showPage()
                    yield page.getpdfdata()

                for area in level['areas']:
                    draw_row(building['name'], level['name'], area['name'])

                    row_index = row_index + 1
                    if row_index == max_rows_per_page:
                        row_index = 0
                        page.showPage()
                        yield page.getpdfdata()

        page.save()
        yield page.getpdfdata()

        buffer.seek(io.SEEK_SET)

        return buffer

    def __get_formatted_list_of_buildings_levels_areas(self):
        location_matrix_items_queryset = LocationMatrix.objects.filter(project=self.validated_data['project'])

        has_building_filter = 'building' in self.validated_data and len(self.validated_data['building']) > 0
        has_level_filter = 'level' in self.validated_data and len(self.validated_data['level']) > 0
        has_area_filter = 'area' in self.validated_data and len(self.validated_data['area']) > 0

        if not has_building_filter and not has_level_filter and not has_area_filter:
            location_matrix_items_queryset = location_matrix_items_queryset.filter(locationmatrixpackage__enabled=True)

        if has_building_filter:
            location_matrix_items_queryset = location_matrix_items_queryset.filter(building__in=self.validated_data['building'])

        if has_level_filter:
            location_matrix_items_queryset = location_matrix_items_queryset.filter(level__in=self.validated_data['level'])

        if has_area_filter:
            location_matrix_items_queryset = location_matrix_items_queryset.filter(area__in=self.validated_data['area'])

        location_matrix_items = LocationMatrixSerializer(
            data=list(location_matrix_items_queryset),
            many=True
        )

        buildings = []
        for location_matrix_item in location_matrix_items.initial_data:
            existing_building_index = find_index(
                buildings,
                lambda x: x['name'] == location_matrix_item.building
            )
            if existing_building_index == -1:
                buildings.append({
                    'name': location_matrix_item.building,
                    'levels': [{
                        'name': location_matrix_item.level,
                        'areas': [{
                            'name': location_matrix_item.area
                        }]
                    }]
                })
                continue

            existing_level_index = find_index(
                buildings[existing_building_index]['levels'],
                lambda x: x['name'] == location_matrix_item.level
            )
            if existing_level_index == -1:
                buildings[existing_building_index]['levels'].append({
                    'name': location_matrix_item.level,
                    'areas': [{
                        'name': location_matrix_item.area
                    }]
                })
                continue

            existing_area_index = find_index(
                buildings[existing_building_index]['levels'][existing_level_index]['areas'],
                lambda x: x['name'] == location_matrix_item.area
            )

            if existing_area_index == -1:
                buildings[existing_building_index]['levels'][existing_level_index]['areas'].append({
                    'name': location_matrix_item.area
                })

        return buildings

    def __generate_qr_code_png(self, project_pk, building_name, level_name, area_name=None):
        data = '{"p":%d,"b":"%s","l":"%s"}' % (project_pk, building_name, level_name) if area_name is None else \
            '{"p":%d,"b":"%s","l":"%s","a":"%s"}' % (project_pk, building_name, level_name, area_name)

        # Hack to remove unicode characters from a string.
        data = data.encode('ascii', 'ignore')
        data = data.decode()

        _, path = tempfile.mkstemp()
        qrcode = pyqrcode.create(data, error='Q')
        qrcode.png(path, scale=10)

        return path

    def __paste_logo_inside_qr_code_png(self, qrcode_path, qr_code_size):
        qrcode_image = Image.open(qrcode_path)
        qrcode_image = qrcode_image.convert('RGBA')
        qrcode_width, qrcode_height = qrcode_image.size
        logo_size = (qrcode_width - qr_code_size) / 4
        logo_image = Image.open('api/static/qr-codes/images/small-logo.png')
        xmin = ymin = int((qrcode_width / 2) - (logo_size / 2))
        xmax = ymax = int((qrcode_width / 2) + (logo_size / 2))
        logo_image = logo_image.resize((xmax - xmin, ymax - ymin))
        qrcode_image.paste(logo_image, (xmin, ymin, xmax, ymax))
        qrcode_image = qrcode_image.transpose(method=Image.ROTATE_90)
        qrcode_image.save(qrcode_path, 'png', quality=100)

    def __drawRotatedText(self, page: canvas.Canvas, text, font, font_size, x, y, box_height, max_lines = 1):
        text_max_width = box_height - 40
        line_x_margin = 7

        text = "\n".join(textwrap.wrap(text, text_max_width)) if max_lines > 1 else self.__truncate_text(page, text, font, font_size, box_height)

        lines = text.splitlines(False)
        len_lines = len(lines)
        for index, line in enumerate(lines):
            line_number = index + 1

            text_width = page.stringWidth(line, font, font_size)
            text_position = y + ((box_height - text_width) / 2)
            text_object = page.beginText()
            text_object.setTextOrigin(0, 0)
            text_object.setFont(font, font_size)

            if line_number == max_lines and len_lines > max_lines:
                line = ' '.join([line, lines[line_number]])
                line = self.__truncate_text(page, line, font, font_size, box_height)

                text_width = page.stringWidth(line, font, font_size)
                text_position = y + ((box_height - text_width) / 2)

            text_object.textLine(text=line)

            page.saveState()
            page.translate(x + index * line_x_margin, text_position)
            page.rotate(90)
            page.drawText(text_object)
            page.restoreState()

            if line_number == max_lines:
                break

    def __truncate_text(self, page, text, font, font_size, max_width):
        text_width = page.stringWidth(text, font, font_size)
        if text_width > max_width:
            for i, c in enumerate(text, start=1):
                new_text = text[0:-i]
                new_text_width = page.stringWidth(new_text, font, font_size)

                if new_text_width < max_width - 5:
                    text = new_text + '...'
                    break

        return text
