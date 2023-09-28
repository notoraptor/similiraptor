import os
from typing import List

from PIL import Image


class Dataset:
    IMAGE_RGB_MODE = "RGB"

    @classmethod
    def open_rgb_image(cls, file_name) -> Image.Image:
        image = Image.open(file_name)
        if image.mode != cls.IMAGE_RGB_MODE:
            image = image.convert(cls.IMAGE_RGB_MODE)
        return image

    @classmethod
    def get_image_paths(cls) -> List[str]:
        dataset_folder = os.path.join(os.path.dirname(__file__), "dataset", "images")
        paths = sorted(
            os.path.join(dataset_folder, name) for name in os.listdir(dataset_folder)
        )
        assert len(paths) == 2105
        return paths
