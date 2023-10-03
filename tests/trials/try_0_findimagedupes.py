"""
Try Linux program findimagedupes

Results:
28 groups
Found 15 / 45 (33.333333333333336 %)
"""
import os
import sys
from tests.utilities import TEST_DIR, generate_similarity_html, SimilarityChecker


def main():
    dupes_path = os.path.join(TEST_DIR, "trials", "findimagedupes.txt")
    assert os.path.isfile(dupes_path)
    similarities = []
    with open(dupes_path) as file:
        i = 1
        for line in file:
            line = line.strip()
            pieces = [
                piece.strip()
                for piece in line.split("dataset/images/")
                if piece.strip()
            ]
            if pieces:
                print(i, pieces, file=sys.stderr)
                i += 1
                similarities.append(pieces)
    groups = [
        [os.path.join(TEST_DIR, "dataset", "images", piece) for piece in pieces]
        for pieces in similarities
    ]
    generate_similarity_html(
        groups, os.path.join(TEST_DIR, "ignored", "try_0_findimagedupes.html")
    )
    chk = SimilarityChecker()
    chk.check(groups)


if __name__ == "__main__":
    main()
