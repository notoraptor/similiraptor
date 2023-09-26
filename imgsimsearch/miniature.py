from collections import namedtuple
from ctypes import c_int

from similiraptor.clibrary import c_int_p
from similiraptor.core import Sequence

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
