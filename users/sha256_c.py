# users/sha256_c.py
import os, ctypes
from ctypes import c_size_t, c_uint8

_lib = ctypes.cdll.LoadLibrary(os.path.join(os.path.dirname(__file__),
                                            'sha256.dll'))
_lib.sha256.argtypes = [ctypes.c_char_p, c_size_t,
                        ctypes.POINTER(c_uint8)]
_lib.sha256.restype  = None

def sha256_c(data: bytes) -> str:
    out = (c_uint8 * 32)()
    _lib.sha256(data, len(data), out)
    return bytes(out).hex()
