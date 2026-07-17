from app.utils import create_folders

from app.pipeline import Pipeline


def main():

    create_folders()

    pipeline = Pipeline()

    pipeline.run()


if __name__ == "__main__":

    main()