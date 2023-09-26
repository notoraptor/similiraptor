from imgsimsearch.miniature import get_miniature, miniature_to_c_sequence
from similiraptor.core import fn_compareSimilarSequences
import sys
from ctypes import pointer
from similiraptor.profiling import Profiler
from PIL import Image


def main():
    assert fn_compareSimilarSequences

    w = 32
    h = 32
    s = (w, h)
    image = Image.new("RGB", s, color=(255, 255, 0))
    image2 = Image.new("RGB", s, color=(255, 255, 255))
    m1 = get_miniature(image)
    m2 = get_miniature(image2)
    s1 = miniature_to_c_sequence(m1)
    s2 = miniature_to_c_sequence(m2)
    ss1 = pointer(s1)
    ss2 = pointer(s2)

    mds = 255 * 3 * w * h
    batch = 20_000
    with Profiler("Native C++"):
        for _ in range(batch):
            c = fn_compareSimilarSequences(ss1, ss2, w, h, mds)
    print(c, file=sys.stderr)


if __name__ == "__main__":
    main()
