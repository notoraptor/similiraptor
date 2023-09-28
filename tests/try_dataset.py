import os

from tests.dataset_provider import Dataset


def main():
    paths = Dataset.get_image_paths()
    print(paths[0])
    assert os.path.isfile(paths[0])
    assert os.path.isfile(paths[-1])


if __name__ == "__main__":
    main()
