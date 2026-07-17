from pathlib import Path
import cv2

from app.pdf_converter import PDFConverter
from app.image_processor import ImageProcessor
from app.table_normalizer import TableNormalizer


class Pipeline:

    def __init__(self):

        self.converter = PDFConverter()
        self.processor = ImageProcessor()
        self.normalizer = TableNormalizer()

    def run(self):

        folders = self.converter.convert_all()

        for folder in folders:

            print(f"\nProcessing {folder.name}")

            pages = sorted(folder.glob("*.png"))

            for page in pages:

                img, gray, binary = self.processor.preprocess(page)

                table = self.normalizer.normalize(
                    img,
                    binary
                )

                output = folder / f"normalized_{page.name}"

                cv2.imwrite(
                    str(output),
                    table
                )

                print("Saved", output)