from pathlib import Path
import fitz
import shutil
import subprocess

from app.config import (
    PDF_DIR,
    OUTPUT_DIR,
    DPI
)


class PDFConverter:

    def convert_all(self, document_paths=None):

        documents = document_paths or [
            *Path(PDF_DIR).glob("*.pdf"),
            *Path(PDF_DIR).glob("*.docx"),
        ]

        converted = []

        for document_path in documents:

            school = document_path.stem

            school_folder = OUTPUT_DIR / school

            school_folder.mkdir(parents=True, exist_ok=True)

            print(f"[{document_path.suffix.upper()[1:]}] {school}")

            pdf_path = document_path
            if document_path.suffix.lower() == ".docx":
                pdf_path = self._convert_docx(document_path, school_folder)

            scale = DPI / 72

            with fitz.open(pdf_path) as document:

                for i, page in enumerate(document, start=1):

                    pixmap = page.get_pixmap(
                        matrix=fitz.Matrix(scale, scale),
                        alpha=False
                    )

                    filename = school_folder / f"page_{i}.png"

                    pixmap.save(str(filename))

            converted.append((school_folder, pdf_path))

        return converted

    @staticmethod
    def extract_identity(pdf_path):
        """Read the school name and ID from the first page's embedded PDF text."""
        with fitz.open(pdf_path) as document:
            text = document[0].get_text()

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        title_index = next(
            (
                index for index, line in enumerate(lines)
                if "SBM" in line.upper() and "ASSESSMENT" in line.upper()
            ),
            None,
        )
        if title_index is None:
            return "", ""

        following = lines[title_index + 1:]
        school_name = next(
            (
                line for line in following[:8]
                if not line.lower().startswith(("name of school", "school id"))
                and not line.replace("-", "").isdigit()
            ),
            "",
        )
        school_id = next(
            (line for line in following[:10] if line.replace("-", "").isdigit()),
            "",
        )
        return school_name, school_id

    @staticmethod
    def _convert_docx(docx_path, output_folder):
        """Convert DOCX while preserving its table layout for image analysis."""
        office = shutil.which("soffice") or shutil.which("libreoffice")
        if office is None:
            raise RuntimeError(
                "DOCX input requires LibreOffice. Install it and ensure 'soffice' "
                "is available on PATH, then run the pipeline again."
            )

        subprocess.run(
            [office, "--headless", "--convert-to", "pdf", "--outdir", str(output_folder), str(docx_path)],
            check=True,
            capture_output=True,
            text=True,
        )
        pdf_path = output_folder / f"{docx_path.stem}.pdf"
        if not pdf_path.exists():
            raise RuntimeError(f"LibreOffice did not create a PDF for {docx_path.name}")
        return pdf_path
