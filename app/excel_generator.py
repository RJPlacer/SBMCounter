from pathlib import Path
from xml.sax.saxutils import escape
import zipfile

from app.config import MANIFESTATIONS


class ExcelGenerator:
    """Create a dependency-free .xlsx report for one processed document."""

    def generate(self, output_path, school_name, school_id, totals, unanswered):
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        headers = ["School name", "School ID", *MANIFESTATIONS, "Unanswered", "Total rows"]
        values = [
            school_name,
            school_id,
            *(totals[heading] for heading in MANIFESTATIONS),
            unanswered,
            sum(totals.values()) + unanswered,
        ]

        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as workbook:
            workbook.writestr("[Content_Types].xml", self._content_types())
            workbook.writestr("_rels/.rels", self._root_rels())
            workbook.writestr("xl/workbook.xml", self._workbook())
            workbook.writestr("xl/_rels/workbook.xml.rels", self._workbook_rels())
            workbook.writestr("xl/worksheets/sheet1.xml", self._sheet(headers, values))

        return output_path

    @staticmethod
    def _cell(value, row, column):
        column_name = ""
        while column:
            column, remainder = divmod(column - 1, 26)
            column_name = chr(65 + remainder) + column_name
        return f'<c r="{column_name}{row}" t="inlineStr"><is><t>{escape(str(value))}</t></is></c>'

    def _sheet(self, headers, values):
        header_cells = "".join(self._cell(value, 1, index) for index, value in enumerate(headers, 1))
        value_cells = "".join(self._cell(value, 2, index) for index, value in enumerate(values, 1))
        last_column = chr(64 + len(headers))
        return (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            '<sheetData><row r="1">' + header_cells + '</row><row r="2">' + value_cells +
            f'</row></sheetData><autoFilter ref="A1:{last_column}2"/></worksheet>'
        )

    @staticmethod
    def _content_types():
        return ('<?xml version="1.0" encoding="UTF-8"?>'
                '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                '<Default Extension="xml" ContentType="application/xml"/>'
                '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
                '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
                '</Types>')

    @staticmethod
    def _root_rels():
        return ('<?xml version="1.0" encoding="UTF-8"?>'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
                '</Relationships>')

    @staticmethod
    def _workbook():
        return ('<?xml version="1.0" encoding="UTF-8"?>'
                '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
                '<sheets><sheet name="Assessment summary" sheetId="1" r:id="rId1"/></sheets></workbook>')

    @staticmethod
    def _workbook_rels():
        return ('<?xml version="1.0" encoding="UTF-8"?>'
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
                '</Relationships>')
