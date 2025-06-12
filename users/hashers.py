# users/hashers.py

import ctypes
import os
import secrets  # Thư viện để tạo salt an toàn
from ctypes import c_size_t, c_uint8
from django.contrib.auth.hashers import BasePasswordHasher
from django.utils.crypto import constant_time_compare

# --- Cấu hình CTypes để gọi thư viện .dll ---
try:
    # Đảm bảo đường dẫn này đúng
    dll = ctypes.cdll.LoadLibrary("lib/sha256.dll") 
    # Khai báo prototype cho hàm sha256
    dll.sha256.argtypes = [ctypes.c_char_p, c_size_t, ctypes.POINTER(c_uint8)]
    dll.sha256.restype = None
    C_AVAILABLE = True
except (OSError, AttributeError):
    print("WARNING: Could not load or configure sha256.dll.")
    C_AVAILABLE = False
# ---------------------------------------------


class CustomSHA256Hasher(BasePasswordHasher):
    """
    Trình băm mật khẩu tùy chỉnh sử dụng SHA-256 từ thư viện C với Salt.
    Định dạng lưu trữ: algorithm$salt$hash
    """
    algorithm = "custom_sha256"

    def _c_sha256(self, data: bytes) -> str:
        """Hàm helper để gọi hàm C và trả về chuỗi hex."""
        if not C_AVAILABLE:
            # Phương án dự phòng nếu không tải được DLL, dùng thư viện của Python
            import hashlib
            return hashlib.sha256(data).hexdigest()

        digest = (c_uint8 * 32)() # 32 bytes = 256 bits
        dll.sha256(data, len(data), digest)
        return bytes(digest).hex()

    def salt(self):
        """Tạo salt ngẫu nhiên an toàn, 16 bytes (32 ký tự hex)."""
        return secrets.token_hex(16)

    def encode(self, password, salt=None):
        """
        Tạo chuỗi hash từ mật khẩu và salt.
        Đây là hàm được gọi khi tạo/thay đổi mật khẩu.
        """
        assert password is not None
        if salt is None:
            salt = self.salt()
        
        # Kết hợp salt và password trước khi băm
        password_bytes = password.encode('utf-8')
        salt_bytes = salt.encode('utf-8')
        
        # Băm (salt + password)
        hash_hex = self._c_sha256(salt_bytes + password_bytes)
        
        # Trả về theo định dạng chuẩn
        return f"{self.algorithm}${salt}${hash_hex}"

    def verify(self, password, encoded):
        """
        Kiểm tra mật khẩu người dùng nhập vào có khớp với chuỗi hash đã lưu không.
        """
        assert password is not None
        try:
            # Tách chuỗi hash đã lưu thành các phần
            algorithm, salt, hash_b = encoded.split('$', 2)
        except ValueError:
            return False # Nếu định dạng sai, không khớp

        if algorithm != self.algorithm:
            return False
        
        # Băm lại mật khẩu người dùng nhập với salt đã lưu
        encoded_2 = self.encode(password, salt)
        _, _, hash_a = encoded_2.split('$', 2)

        # So sánh an toàn để chống tấn công timing attack
        return constant_time_compare(hash_a, hash_b)

    def safe_summary(self, encoded):
        """Tạo bản tóm tắt an toàn để hiển thị trong trang admin."""
        algorithm, salt, hash_val = encoded.split('$', 2)
        return {
            'algorithm': algorithm,
            'salt': salt,
            'hash': hash_val,
        }