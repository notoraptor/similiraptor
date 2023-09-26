from similiraptor.core import fn_compareSimilarSequences
import sys
from ctypes import pointer, c_int
from similiraptor.profiling import Profiler
from similiraptor.clibrary import c_int_p
from similiraptor.core import Sequence
from PIL import Image
from collections import namedtuple

Miniature = namedtuple("Miniature", ("r", "g", "b"))


def get_miniature(thumbnail):
    r, g, b = thumbnail.split()
    return Miniature(r.tobytes(), g.tobytes(), b.tobytes())


def miniature_to_c_sequence(self):
    array_type = c_int * len(self.r)
    return Sequence(
        c_int_p(array_type(*self.r)),
        c_int_p(array_type(*self.g)),
        c_int_p(array_type(*self.b)),
    )


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


if __name__ == '__main__':
    main()
