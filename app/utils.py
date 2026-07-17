from pathlib import Path


def create_folders():

    folders = [

        "output",

        "reports",

        "templates"

    ]

    for folder in folders:

        Path(folder).mkdir(exist_ok=True)


def school_name(pdf):

    return Path(pdf).stem