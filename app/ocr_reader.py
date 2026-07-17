import cv2
import pytesseract
import re
import os
from pathlib import Path
import shutil

from app.models import SBMAssessment


class OCRReader:

    def __init__(self):

        # Change this if Tesseract is installed elsewhere
        executable = (
            os.environ.get("TESSERACT_CMD")
            or shutil.which("tesseract")
            or r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        )
        if not Path(executable).is_file():
            raise RuntimeError(
                "Tesseract OCR was not found. Add it to PATH or set TESSERACT_CMD "
                "to the full path of tesseract.exe."
            )
        pytesseract.pytesseract.tesseract_cmd = executable

    def extract(self, image):

        assessment = SBMAssessment()

        # -----------------------------
        # Crop School Name region
        # -----------------------------
        name_roi = image[
            120:220,
            200:1200
        ]

        # -----------------------------
        # Crop School ID region
        # -----------------------------
        id_roi = image[
            120:220,
            1400:1900
        ]

        name_text = pytesseract.image_to_string(
            name_roi,
            config="--psm 7"
        ).strip()

        id_text = pytesseract.image_to_string(
            id_roi,
            config="--psm 7 digits"
        ).strip()

        assessment.school_name = name_text

        match = re.search(r"\d+", id_text)

        if match:
            assessment.school_id = match.group()

        return assessment
