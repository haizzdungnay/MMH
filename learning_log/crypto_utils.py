# learning_log/crypto_utils.py

import ctypes
import json
import time
from ctypes import c_size_t, c_uint8, c_uint64, POINTER
from functools import wraps

from django.conf import settings
from django.contrib.auth.models import User
from django.http import JsonResponse

# Cần import model Profile từ app 'users'
from users.models import Profile

# --- 1. Load thư viện DLL ---
# !!! LƯU Ý: Đảm bảo đường dẫn này chính xác so với vị trí bạn chạy `manage.py`
try:
    dll = ctypes.cdll.LoadLibrary("lib/sha256.dll")
except OSError:
    # Fallback an toàn nếu không load được DLL, dùng thư viện chuẩn của Python
    # Điều này giúp project vẫn chạy được dù không có file .dll
    print("WARNING: Could not load sha256.dll. Falling back to Python's hashlib.")
    dll = None

# --- 2. Khai báo prototype cho các hàm ---
if dll:
    dll.sha256.argtypes = [ctypes.c_char_p, c_size_t, POINTER(c_uint8)]
    dll.sha256.restype = None

    dll.hmac_sha256.argtypes = [
        ctypes.c_char_p, c_size_t,    # key, keylen
        ctypes.c_char_p, c_size_t,    # msg, msglen
        c_uint64,                    # timestamp
        POINTER(c_uint8)             # output buffer
    ]
    dll.hmac_sha256.restype = None

# --- 3. Wrapper trên Python ---
def sha256_c(data: bytes) -> str:
    if not dll:
        import hashlib
        return hashlib.sha256(data).hexdigest()
    out = (c_uint8 * 32)()
    dll.sha256(data, len(data), out)
    return bytes(out).hex()

def hmac_sha256_c(key: bytes, msg: bytes, timestamp: int) -> str:
    if not dll:
        import hmac
        import hashlib
        import struct
        ts_le = struct.pack("<Q", timestamp)
        return hmac.new(key, msg + ts_le, hashlib.sha256).hexdigest()
    out = (c_uint8 * 32)()
    dll.hmac_sha256(key, len(key), msg, len(msg), timestamp, out)
    return bytes(out).hex()


# --- 4. Decorator để xác thực Token ---
def token_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Lấy thông tin từ request body (giả định client gửi JSON)
        try:
            # Dùng request.POST nếu client gửi form-data, hoặc request.headers nếu gửi qua header
            auth_data = json.loads(request.body)
            token = auth_data.get('token')
            user_id = auth_data.get('user_id')
            timestamp = auth_data.get('timestamp')

            if not all([token, user_id, timestamp]):
                return JsonResponse({'error': 'Missing authentication data'}, status=401)

        except (json.JSONDecodeError, AttributeError):
             return JsonResponse({'error': 'Invalid or missing authentication data in body'}, status=401)

        # 1. Kiểm tra timestamp để chống Replay Attack (Token chỉ hợp lệ trong 5 phút)
        if int(time.time()) - int(timestamp) > 300:
             return JsonResponse({'error': 'Token has expired'}, status=401)

        # 2. Lấy user và secret key từ DB
        try:
            user = User.objects.get(id=user_id)
            # Lấy secret key từ profile của user trong DB
            user_secret_key = user.profile.secret_key.encode('utf-8')

        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=401)
        except Profile.DoesNotExist:
            # Lỗi này không nên xảy ra nếu signal hoạt động đúng
            return JsonResponse({'error': 'Critical: User profile or secret key not found'}, status=500)

        # 3. Tái tạo token và so sánh
        user_id_bytes = str(user.id).encode('utf-8')
        expected_token = hmac_sha256_c(user_secret_key, user_id_bytes, int(timestamp))

        if token != expected_token:
            return JsonResponse({'error': 'Invalid token'}, status=401)

        # Gắn user vào request để view có thể sử dụng nếu cần
        request.user = user

        # Nếu mọi thứ hợp lệ, chạy view gốc
        return view_func(request, *args, **kwargs)

    return wrapper