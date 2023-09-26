from similiraptor.core import fn_compareSimilarSequences, image_to_native
import sys
from ctypes import pointer
from tests.profiling import Profiler
from PIL import Image


def main():
    assert fn_compareSimilarSequences

    w = 32
    h = 32
    s = (w, h)
    image1 = Image.new("RGB", s, color=(255, 255, 0))
    image2 = Image.new("RGB", s, color=(255, 255, 255))
    s1 = image_to_native(image1)
    s2 = image_to_native(image2)
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
