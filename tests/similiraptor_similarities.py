from typing import Iterable, Tuple, Any

from PIL.Image import Image

from tests.utilities import SimilarityChecker, generate_similarity_html, ImageUtils
from imgsimsearch.abstract_image_provider import AbstractImageProvider
from imgsimsearch import search_similar_images
from tests.dataset import Dataset
from tests.profiling import Profiler


class DatasetImageProvider(AbstractImageProvider):
    def __init__(self):
        self.image_paths = Dataset.get_image_paths()

    def count(self) -> int:
        return len(self.image_paths)

    def items(self) -> Iterable[Tuple[Any, Image]]:
        for path in self.image_paths:
            yield path, ImageUtils.open_rgb_image(path)


def main():
    dip = DatasetImageProvider()
    groups = [sorted(values) for values in search_similar_images(dip)]
    generate_similarity_html(groups, "ignored/similiraptor_results.html")
    chk = SimilarityChecker()
    chk.check(groups)


if __name__ == "__main__":
    with Profiler("Similiraptor script"):
        main()
