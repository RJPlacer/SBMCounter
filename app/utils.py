from pathlib import Path

from app.config import OUTPUT_DIR, REPORT_DIR, UPLOAD_DIR, TEMPLATE_DIR


def create_folders():
    """Create every working folder at the same absolute paths config.py uses.

    Previously this created folders named "output", "reports", etc. relative
    to the current working directory, which silently diverged from
    config.OUTPUT_DIR / config.REPORT_DIR whenever main.py was launched from
    somewhere other than the project root.
    """

    for folder in (OUTPUT_DIR, REPORT_DIR, UPLOAD_DIR, TEMPLATE_DIR):
        folder.mkdir(parents=True, exist_ok=True)


def school_name(pdf):

    return Path(pdf).stem
