import argparse

from app.utils import create_folders


def main():

    create_folders()

    parser = argparse.ArgumentParser(description="Generate SBM checklist reports.")
    parser.add_argument("--web", action="store_true", help="start the browser upload interface")
    args = parser.parse_args()

    if args.web:
        from app.web import run_server
        run_server()
        return

    from app.pipeline import Pipeline
    pipeline = Pipeline()

    pipeline.run()


if __name__ == "__main__":

    main()
