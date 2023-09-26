from ctypes import pointer
from typing import Dict, Any, Sequence, List, Set

from tqdm import tqdm

from imgsimsearch.abstract_image_provider import AbstractImageProvider
from imgsimsearch.graph import Graph
from similiraptor.core import fn_compareSimilarSequences, image_to_native

SIM_LIMIT = 0.89
SIMPLE_MAX_PIXEL_DISTANCE = 255 * 3
THUMBNAIL_DIMENSION = 32
THUMBNAIL_SIZE = (THUMBNAIL_DIMENSION, THUMBNAIL_DIMENSION)


class CppSimilarityComparator:
    __slots__ = ("max_dst_score", "limit", "width", "height")

    def __init__(self, limit, width, height):
        self.width = width
        self.height = height
        self.limit = limit
        self.max_dst_score = SIMPLE_MAX_PIXEL_DISTANCE * width * height

    def are_similar(self, p1, p2) -> bool:
        return (
            fn_compareSimilarSequences(
                p1, p2, self.width, self.height, self.max_dst_score
            )
            >= self.limit
        )


def compare_images_native(
    imp: AbstractImageProvider, output: Dict[Any, Sequence[Any]]
) -> List[Set[Any]]:
    nb_images = imp.count()
    native_sequences = {}
    native_sequence_pointers = {}
    with tqdm(total=nb_images, desc="Generate numpy miniatures") as pbar:
        for identifier, image in imp.items():
            sequence = image_to_native(image.resize(THUMBNAIL_SIZE))
            native_sequences[identifier] = sequence
            native_sequence_pointers[identifier] = pointer(sequence)
            pbar.update(1)
    assert len(native_sequences) == nb_images

    graph = Graph()
    nb_todo = sum(len(d) for d in output.values())
    sim_cmp = CppSimilarityComparator(
        SIM_LIMIT, THUMBNAIL_DIMENSION, THUMBNAIL_DIMENSION
    )
    with tqdm(total=nb_todo, desc="Make real comparisons using Numpy") as bar:
        for filename, linked_filenames in output.items():
            p1 = native_sequence_pointers[filename]
            for linked_filename in linked_filenames:
                p2 = native_sequence_pointers[linked_filename]
                if sim_cmp.are_similar(p1, p2):
                    graph.connect(filename, linked_filename)
                bar.update(1)

    groups = [group for group in graph.pop_groups() if len(group) > 1]
    return groups
