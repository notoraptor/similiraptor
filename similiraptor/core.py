from ctypes import POINTER, Structure, c_double, c_int
from similiraptor.clibrary import CLibrary, c_int_p
from similiraptor.system import System
import os


class Sequence(Structure):
    _fields_ = [("r", c_int_p), ("g", c_int_p), ("b", c_int_p)]


PtrSequence = POINTER(Sequence)

_native_library = CLibrary(
    os.path.join(
        os.path.dirname(__file__), System.get_lib_basename("similiraptor", prefix="")
    )
)

fn_compareSimilarSequences = _native_library.prototype(
    "compareSimilarSequences", c_double, [PtrSequence, PtrSequence, c_int, c_int, c_int]
)
