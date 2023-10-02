import json
import os
import sys
from ctypes import pointer

from PIL import ImageOps
from tqdm import tqdm

from imgsimsearch.native_fine_comparator import (
    CppSimilarityComparator,
    SIM_LIMIT,
    THUMBNAIL_DIMENSION,
    THUMBNAIL_SIZE,
    image_to_native,
)
from tests.dataset import Dataset
from tests.profiling import Profiler
from tests.utilities import (
    ImageUtils,
    SimilarityChecker,
    TEST_DIR,
    generate_similarity_html,
)

OUTPUT_BASENAME = "brute_force_results"
OUTPUT_JSON_PATH = os.path.join(TEST_DIR, "ignored", f"{OUTPUT_BASENAME}.json")
OUTPUT_HTML_PATH = os.path.join(TEST_DIR, "ignored", f"{OUTPUT_BASENAME}.html")


def main():
    sim_cmp = CppSimilarityComparator(
        SIM_LIMIT, THUMBNAIL_DIMENSION, THUMBNAIL_DIMENSION
    )
    image_paths = Dataset.get_image_paths()
    sequences = [
        image_to_native(
            ImageOps.equalize(ImageUtils.open_rgb_image(path)).resize(THUMBNAIL_SIZE)
        )
        for path in tqdm(image_paths, desc="Generate native sequences")
    ]
    sequence_pointers = [
        pointer(sequence)
        for sequence in tqdm(sequences, desc="Generate native sequence pointers")
    ]
    nb_images = len(image_paths)
    nb_computations = nb_images * (nb_images - 1) // 2
    groups = []

    print("Brute force comparisons to do:", nb_computations, file=sys.stderr)
    with tqdm(total=nb_computations, desc="Brute force similarity search") as pbar:
        for i in range(nb_images):
            nears = []
            for j in range(i + 1, nb_images):
                if sim_cmp.are_similar(sequence_pointers[i], sequence_pointers[j]):
                    nears.append(j)
                pbar.update(1)
            if nears:
                groups.append([image_paths[i]] + sorted(image_paths[j] for j in nears))

    with open(OUTPUT_JSON_PATH, "w") as file:
        json.dump(groups, file, indent=1)
    print(
        "JSON: Saved",
        len(groups),
        f"similarity groups ({sum(len(group) for group in groups)} images) in",
        OUTPUT_JSON_PATH,
        file=sys.stderr,
    )
    generate_similarity_html(groups, OUTPUT_HTML_PATH)
    chk = SimilarityChecker()
    chk.check(groups)


if __name__ == "__main__":
    with Profiler("Brute force script"):
        main()
