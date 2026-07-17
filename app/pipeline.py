import cv2

from app.config import REPORT_DIR
from app.counter import Counter
from app.excel_generator import ExcelGenerator
from app.pdf_converter import PDFConverter
from app.image_processor import ImageProcessor
from app.table_normalizer import TableNormalizer
from app.checkbox_detector import CheckboxDetector


class Pipeline:

    def __init__(self):

        self.converter = PDFConverter()
        self.processor = ImageProcessor()
        self.normalizer = TableNormalizer()
        self.detector = CheckboxDetector()
        self.excel = ExcelGenerator()

    def run(self, document_paths=None):

        folders = self.converter.convert_all(document_paths)
        reports = []

        for folder, pdf_path in folders:

            print(f"\nProcessing {folder.name}")
            counter = Counter()
            school_name = folder.name
            school_id = ""
            extracted_name, extracted_id = self.converter.extract_identity(pdf_path)
            school_name = extracted_name or school_name
            school_id = extracted_id

            pages = sorted(folder.glob("page_*.png"))
            failed_pages = []

            for page in pages:

                print(f"Processing {page.name}")

                try:
                    img, gray, binary = self.processor.preprocess(page)

                    table = self.normalizer.normalize(
                        img,
                        binary
                    )

                    responses = self.detector.detect_page(table)
                    counter.add_page(responses)

                    for i, response in enumerate(responses, start=1):
                        print(f"{i:02d}. {response}")

                    output = folder / f"normalized_{page.name}"

                    cv2.imwrite(
                        str(output),
                        table
                    )

                    print("Saved", output)

                except Exception as error:
                    # One warped/blank/misprinted page shouldn't take down the
                    # whole school's report -- log it, skip it, and keep going.
                    print(f"  Skipped {page.name}: {error}")
                    failed_pages.append(page.name)
                    continue

            if failed_pages:
                print(
                    f"Warning: {len(failed_pages)} page(s) could not be read "
                    f"for {folder.name}: {', '.join(failed_pages)}"
                )

            report = self.excel.generate(
                REPORT_DIR / f"{folder.name}_report.xlsx",
                school_name,
                school_id,
                counter.totals(),
                counter.unanswered(),
            )
            print("Report saved", report)
            reports.append(report)

        return reports
