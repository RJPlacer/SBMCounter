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

POPPLER_PATH = r"C:\poppler\Library\bin"

# ===============================
# IMAGE SETTINGS
# ===============================

DPI = 400

THRESHOLD = 0

MIN_TABLE_AREA = 1_000_000

# ===============================
# CHECKBOX SETTINGS
# ===============================

CHECKBOX_SIZE = 26

MARK_THRESHOLD = 0.18

ROW_COUNT = 42

COLUMN_COUNT = 4

# The headings in the source checklist, ordered from left to right.
MANIFESTATIONS = (
    "Always manifested",
    "Frequently manifested",
    "Rarely manifested",
    "Not yet manifested",
)
