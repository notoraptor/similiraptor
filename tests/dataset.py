import os
from typing import List


class Dataset:
    @classmethod
    def get_image_paths(cls) -> List[str]:
        dataset_folder = os.path.join(os.path.dirname(__file__), "dataset", "images")
        paths = sorted(
            os.path.join(dataset_folder, name) for name in os.listdir(dataset_folder)
        )
        assert len(paths) == 2105
        return paths
