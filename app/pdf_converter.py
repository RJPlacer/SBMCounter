from pathlib import Path
from pdf2image import convert_from_path

from app.config import (
    PDF_DIR,
    OUTPUT_DIR,
    POPPLER_PATH,
    DPI
)


class PDFConverter:

    def convert_all(self):

        pdfs = list(Path(PDF_DIR).glob("*.pdf"))

        converted = []

        for pdf in pdfs:

            school = pdf.stem

            school_folder = OUTPUT_DIR / school

            school_folder.mkdir(parents=True, exist_ok=True)

            print(f"[PDF] {school}")

            pages = convert_from_path(
                str(pdf),
                dpi=DPI,
                poppler_path=POPPLER_PATH
            )

            for i, page in enumerate(pages, start=1):

                filename = school_folder / f"page_{i}.png"

                page.save(filename)

            converted.append(school_folder)

        return converted