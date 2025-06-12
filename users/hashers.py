# users/hashers.py

import hashlib
import secrets
from django.contrib.auth.hashers import BasePasswordHasher
from django.utils.crypto import constant_time_compare

class CustomSHA256Hasher(BasePasswordHasher):
    """
    Trình băm mật khẩu tùy chỉnh sử dụng SHA-256 có sẵn của Python với Salt.
    Định dạng lưu trữ trong database sẽ là: algorithm$salt$hash
    """
    # Tên định danh cho thuật toán, sẽ được lưu trong chuỗi hash
    algorithm = "custom_sha256"

    def salt(self):
        """
        Tạo ra một chuỗi "salt" (muối) ngẫu nhiên, an toàn về mặt mật mã học.
        Salt dùng để đảm bảo hai mật khẩu giống nhau sẽ có hash khác nhau.
        """
        return secrets.token_hex(16)  # Tạo salt dài 32 ký tự hex

    def encode(self, password, salt=None):
        """
        Đây là hàm được gọi khi người dùng tạo mới hoặc thay đổi mật khẩu.
        Nó nhận mật khẩu thô (raw password) và tạo ra chuỗi hash để lưu vào database.
        """
        # Đảm bảo mật khẩu không rỗng
        assert password is not None
        # Nếu chưa có salt, tạo một salt mới
        if salt is None:
            salt = self.salt()
        
        # Chuyển mật khẩu và salt sang dạng bytes
        password_bytes = password.encode('utf-8')
        salt_bytes = salt.encode('utf-8')
        
        # Sử dụng thư viện hashlib của Python để băm SHA-256
        # Công thức: hash = SHA256(salt + password)
        hash_obj = hashlib.sha256(salt_bytes + password_bytes)
        hash_hex = hash_obj.hexdigest()
        
        # Trả về chuỗi hash hoàn chỉnh theo định dạng để lưu trữ
        return f"{self.algorithm}${salt}${hash_hex}"

    def verify(self, password, encoded):
        """
        Đây là hàm được gọi khi người dùng đăng nhập.
        Nó so sánh mật khẩu người dùng nhập vào với chuỗi hash trong database.
        """
        assert password is not None
        try:
            # Tách chuỗi hash đã lưu thành 3 phần: thuật toán, salt, và hash
            algorithm, salt, hash_db = encoded.split('$', 2)
        except ValueError:
            # Nếu chuỗi trong DB không đúng định dạng, trả về False
            return False

        # Kiểm tra xem có đúng là thuật toán của chúng ta không
        if algorithm != self.algorithm:
            return False
        
        # Băm lại mật khẩu mà người dùng vừa nhập với salt đã được lưu từ trước
        # để xem kết quả có khớp không.
        encoded_2 = self.encode(password, salt)
        _, _, hash_input = encoded_2.split('$', 2)

        # Sử dụng hàm so sánh an toàn để chống "timing attacks"
        return constant_time_compare(hash_input, hash_db)

    def safe_summary(self, encoded):
        """
        Tạo một bản tóm tắt an toàn về chuỗi hash để hiển thị trong trang admin của Django.
        """
        algorithm, salt, hash_val = encoded.split('$', 2)
        return {
            'algorithm': algorithm,
            'salt': salt,
            'hash': hash_val,
        }