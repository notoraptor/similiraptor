import json
import sys
from ctypes import pointer

from tqdm import tqdm

from imgsimsearch.graph import Graph
from imgsimsearch.native_fine_comparator import (
    CppSimilarityComparator,
    SIM_LIMIT,
    THUMBNAIL_DIMENSION,
    THUMBNAIL_SIZE,
    image_to_native,
)
from tests.dataset_provider import Dataset
from tests.profiling import Profiler
from tests.similarity_json_to_html import OUTPUT_JSON_PATH


def main():
    sim_cmp = CppSimilarityComparator(
        SIM_LIMIT, THUMBNAIL_DIMENSION, THUMBNAIL_DIMENSION
    )
    image_paths = Dataset.get_image_paths()
    sequences = [
        image_to_native(Dataset.open_rgb_image(path).resize(THUMBNAIL_SIZE))
        for path in tqdm(image_paths, desc="Generate native sequences")
    ]
    sequence_pointers = [
        pointer(sequence)
        for sequence in tqdm(sequences, desc="Generate native sequence pointers")
    ]
    nb_images = len(image_paths)
    nb_computations = nb_images * (nb_images - 1) // 2
    graph = Graph()

    print("Brute force comparisons to do:", nb_computations, file=sys.stderr)
    with tqdm(total=nb_computations, desc="Brute force similarity search") as pbar:
        for i in range(nb_images):
            for j in range(i + 1, nb_images):
                if sim_cmp.are_similar(sequence_pointers[i], sequence_pointers[j]):
                    graph.connect(image_paths[i], image_paths[j])
                pbar.update(1)

    groups = [sorted(group) for group in graph.pop_groups() if len(group) > 1]

    with open(OUTPUT_JSON_PATH, "w") as file:
        json.dump(groups, file, indent=1)
    print(
        "Saved",
        len(groups),
        f"similarity groups ({sum(len(group) for group in groups)} images) in",
        OUTPUT_JSON_PATH,
        file=sys.stderr,
    )


if __name__ == "__main__":
    with Profiler("Brute force script"):
        main()
