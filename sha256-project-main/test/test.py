import ctypes
import hashlib
import hmac
import struct
import time
import os
from ctypes import c_size_t, c_uint8, c_uint64, POINTER

# --- 1. Load thư viện DLL ---
dll = ctypes.cdll.LoadLibrary("../lib/sha256.dll")  # đổi thành đường dẫn DLL thực tế của bạn

# --- 2. Khai báo prototype cho các hàm ---
dll.sha256.argtypes = [ctypes.c_char_p, c_size_t, POINTER(c_uint8)]
dll.sha256.restype = None

dll.hmac_sha256.argtypes = [
    ctypes.c_char_p, c_size_t,   # key, keylen
    ctypes.c_char_p, c_size_t,   # msg, msglen
    c_uint64,                     # timestamp
    POINTER(c_uint8)              # output buffer
]
dll.hmac_sha256.restype = None

# --- 3. Wrapper trên Python ---
def sha256_c(data: bytes) -> str:
    out = (c_uint8 * 32)()
    dll.sha256(data, len(data), out)
    return bytes(out).hex()

def hmac_sha256_c(key: bytes, msg: bytes, timestamp: int) -> str:
    out = (c_uint8 * 32)()
    dll.hmac_sha256(key, len(key), msg, len(msg), timestamp, out)
    return bytes(out).hex()

# --- 4. Hàm test với format đẹp ---
def test_sha256_case(data: bytes):
    py_hash = hashlib.sha256(data).hexdigest()
    c_hash  = sha256_c(data)
    ok = py_hash == c_hash
    print(f"Input       : {data!r}")
    print(f"  Python SHA256 : {py_hash}")
    print(f"  DLL    SHA256 : {c_hash}")
    print(f"  Result         : {'OK ✅' if ok else 'FAIL ❌'}\n")

def test_hmac_case(key: bytes, msg: bytes, ts: int):
    ts_le = struct.pack("<Q", ts)  # little-endian match C trên Windows
    py_hmac = hmac.new(key, msg + ts_le, hashlib.sha256).hexdigest()
    c_hmac  = hmac_sha256_c(key, msg, ts)
    ok = py_hmac == c_hmac

    print(f"Key length  : {len(key)}")
    print(f"Key         : {key[:32]!r}{'...' if len(key)>32 else ''}")
    print(f"Message     : {msg!r}")
    print(f"Timestamp   : {ts}")
    print(f"  Python HMAC  : {py_hmac}")
    print(f"  DLL    HMAC  : {c_hmac}")
    print(f"  Result        : {'OK ✅' if ok else 'FAIL ❌'}\n")

if __name__ == "__main__":
    # SHA256 cơ bản
    print("="*60)
    print(" SHA256 Tests ".center(60, "="))
    print("="*60, "\n")
    for data in [b"abc", b"The quick brown fox jumps over the lazy dog", b""]:
        test_sha256_case(data)

    # HMAC-SHA256 với các key khác nhau
    print("="*60)
    print(" HMAC-SHA256 with Various Keys ".center(60, "="))
    print("="*60, "\n")
    now = int(time.time())
    messages = [b"message", b"hello world", b"", os.urandom(50)]
    keys = [
        b"",                  # 0 bytes
        b"a",                 # 1 byte
        b"A"*63,              # 63 bytes
        b"B"*64,              # 64 bytes (block size)
        b"C"*65,              # 65 bytes (> block size)
        b"D"*100,             # 100 bytes
        os.urandom(128),      # random 128 bytes
    ]

    for key in keys:
        for msg in messages:
            test_hmac_case(key, msg, now)
