import os
from pathlib import Path

# ===============================
# PATHS
# ===============================

ROOT = Path(__file__).resolve().parent.parent

PDF_DIR = ROOT / "pdfs"

OUTPUT_DIR = ROOT / "output"

REPORT_DIR = ROOT / "reports"

TEMPLATE_DIR = ROOT / "templates"

UPLOAD_DIR = ROOT / "uploads"

# Only needed on Windows, where poppler usually isn't on PATH. Leave unset
# (None) on Linux/Mac/CI so pdf2image/PyMuPDF-adjacent tools fall back to
# whatever poppler is already on PATH. Override with an env var instead of
# editing this file, so the same code runs on every machine.
POPPLER_PATH = os.environ.get("POPPLER_PATH") or (
    r"C:\poppler\Library\bin" if os.name == "nt" else None
)
# NOTE: the previous config.py had MARK_THRESHOLD = 0.18, but
# checkbox_detector.py actually ran on a hardcoded 0.05 (comment: thin ticks
# need a lower bar). 0.05 is the value proven out in practice, so it's kept
# below as the real default instead of the untested 0.18.

# ===============================
# IMAGE SETTINGS
# ===============================

DPI = 400

THRESHOLD = 0

MIN_TABLE_AREA = 1_000_000

# Standardized normalized table image size. TableNormalizer and CheckboxGrid
# both used to hardcode this separately -- keep it here as the one source.
NORMALIZED_WIDTH = 2200
NORMALIZED_HEIGHT = 3200

# ===============================
# CHECKBOX SETTINGS
# ===============================

# Used by CheckboxGrid for a fixed-offset fallback layout and by
# CheckboxDetector as a size filter when it finds boxes dynamically.
CHECKBOX_SIZE = 26

# Minimum fraction of a checkbox's interior that must be dark ink for it to
# count as marked. Read by CheckboxDetector; don't hardcode this elsewhere.
MARK_THRESHOLD = 0.05

ROW_COUNT = 42

COLUMN_COUNT = 4

# The headings in the source checklist, ordered from left to right.
MANIFESTATIONS = (
    "Always manifested",
    "Frequently manifested",
    "Rarely manifested",
    "Not yet manifested",
)
